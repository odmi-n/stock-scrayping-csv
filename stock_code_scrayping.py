import requests
from bs4 import BeautifulSoup
import re
import random
import argparse
import sys
import threading
from typing import List, Optional, Tuple

import tkinter as tk
from tkinter import ttk, messagebox

import yfinance as yf

def scrape_stock_codes(url):
    """
    指定されたURLから東証の全銘柄コードをスクレイピングする。
    ページ内のテーブルから銘柄コード、銘柄名、市場情報を抽出し、
    REITを除外した銘柄のみを返す。
    """
    response = requests.get(url)
    if response.status_code != 200:
        raise Exception("ページの取得に失敗しました。")
    
    soup = BeautifulSoup(response.text, 'html.parser')
    codes = []
    
    # テーブルの行を取得
    table_rows = soup.find_all('tr')
    
    for row in table_rows:
        cells = row.find_all('td')
        if len(cells) >= 4:  # コード、銘柄名、業種、市場の4列があることを確認
            # 最初のセルからコードを抽出
            code_cell = cells[0]
            code_link = code_cell.find('a', href=True)
            if code_link:
                match = re.search(r'/stock/([0-9]+[A-Z]*)', code_link['href'])
                if match:
                    code = match.group(1).strip()
                    
                    # 市場情報を取得（4番目のセル）
                    market = cells[3].get_text(strip=True)
                    
                    # REITを除外（市場名に「REIT」が含まれる場合は除外）
                    if 'REIT' not in market:
                        codes.append(code)
    
    return codes

def filter_valid_codes(codes):
    """
    取得した銘柄コードのうち、数値部分が1301以上のもののみを返す。
    英字を含む銘柄コード（130A等）も対象とする。
    ※これによりETFやREIT等、意図しないコードを除外する。
    """
    valid = []
    for code in codes:
        # 数字部分を抽出（先頭の数字のみ）
        numeric_part = re.match(r'(\d+)', code)
        if numeric_part:
            numeric_value = int(numeric_part.group(1))
            if numeric_value >= 1301:
                valid.append(code)
    return valid



def fetch_latest_close(code: str) -> Optional[float]:
    """yfinanceを利用して指定銘柄の直近終値を取得する。"""
    if not code or not code.isdigit():
        return None

    ticker = f"{code}.T"
    try:
        history = yf.Ticker(ticker).history(period="5d", auto_adjust=False, prepost=False)
        if history.empty:
            history = yf.download(ticker, period="5d", progress=False)
        if history.empty:
            return None

        closes = history["Close"].dropna()
        if closes.empty:
            return None
        return float(closes.iloc[-1])
    except Exception:
        return None


def select_codes_by_price(
    codes: List[str], count: int, min_price: float, max_price: float
) -> List[Tuple[str, float]]:
    """価格条件を満たす銘柄コードを抽出する。"""

    filtered: List[Tuple[str, float]] = []
    shuffled_codes = codes[:]
    random.shuffle(shuffled_codes)

    for code in shuffled_codes:
        if len(filtered) >= count:
            break

        close_price = fetch_latest_close(code)
        if close_price is None:
            continue

        if min_price <= close_price <= max_price:
            display_code = code.zfill(4) if code.isdigit() else code
            filtered.append((display_code, close_price))

    return filtered


class StockScraperApp:
    def __init__(self, master: tk.Tk) -> None:
        self.master = master
        self.master.title("銘柄コードスクレイパー")

        self.count_var = tk.StringVar(value="30")
        self.min_price_var = tk.StringVar(value="100")
        self.max_price_var = tk.StringVar(value="500")

        self._build_widgets()

    def _build_widgets(self) -> None:
        self.master.columnconfigure(0, weight=1)
        self.master.rowconfigure(1, weight=1)

        controls = ttk.Frame(self.master, padding=(10, 10, 10, 0))
        controls.grid(row=0, column=0, sticky="ew")
        controls.columnconfigure(1, weight=1)

        ttk.Label(controls, text="抽出銘柄数").grid(row=0, column=0, sticky="w", padx=(0, 10), pady=5)
        ttk.Entry(controls, textvariable=self.count_var, width=10).grid(
            row=0, column=1, sticky="ew", pady=5
        )

        ttk.Label(controls, text="終値下限 (円)").grid(row=1, column=0, sticky="w", padx=(0, 10), pady=5)
        ttk.Entry(controls, textvariable=self.min_price_var, width=10).grid(
            row=1, column=1, sticky="ew", pady=5
        )

        ttk.Label(controls, text="終値上限 (円)").grid(row=2, column=0, sticky="w", padx=(0, 10), pady=5)
        ttk.Entry(controls, textvariable=self.max_price_var, width=10).grid(
            row=2, column=1, sticky="ew", pady=5
        )

        self.start_button = ttk.Button(
            controls, text="スクレイピング開始", command=self.start_scraping
        )
        self.start_button.grid(row=3, column=0, columnspan=2, pady=(10, 5))

        self.status_var = tk.StringVar(value="準備完了")
        ttk.Label(controls, textvariable=self.status_var).grid(
            row=4, column=0, columnspan=2, sticky="w", pady=(0, 5)
        )

        table_frame = ttk.Frame(self.master, padding=(10, 5, 10, 10))
        table_frame.grid(row=1, column=0, sticky="nsew")
        table_frame.columnconfigure(0, weight=1)
        table_frame.rowconfigure(0, weight=1)

        columns = ("code", "price")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=15)
        self.tree.heading("code", text="銘柄コード")
        self.tree.heading("price", text="終値 (円)")
        self.tree.column("code", width=120, anchor="center")
        self.tree.column("price", width=120, anchor="e")
        self.tree.grid(row=0, column=0, sticky="nsew")

        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.grid(row=0, column=1, sticky="ns")

    def start_scraping(self) -> None:
        try:
            count = int(self.count_var.get())
            if count <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("入力エラー", "抽出銘柄数は正の整数を入力してください。")
            return

        try:
            min_price = float(self.min_price_var.get())
            max_price = float(self.max_price_var.get())
        except ValueError:
            messagebox.showerror("入力エラー", "終値の範囲には数値を入力してください。")
            return

        if min_price > max_price:
            messagebox.showerror("入力エラー", "終値の下限は上限以下である必要があります。")
            return

        self.status_var.set("スクレイピング中...")
        self.start_button.config(state=tk.DISABLED)

        threading.Thread(
            target=self._scrape_in_thread,
            args=(count, min_price, max_price),
            daemon=True,
        ).start()

    def _scrape_in_thread(self, count: int, min_price: float, max_price: float) -> None:
        url = "https://nikkeiyosoku.com/stock/all/"

        try:
            codes = scrape_stock_codes(url)
            valid_codes = filter_valid_codes(codes)
        except Exception as exc:
            self.master.after(0, self._handle_error, f"スクレイピングに失敗しました: {exc}")
            return

        if not valid_codes:
            self.master.after(0, self._handle_error, "有効な銘柄コードが見つかりませんでした。")
            return

        results = select_codes_by_price(valid_codes, count, min_price, max_price)

        self.master.after(0, self._update_results, results, count, len(valid_codes))

    def _handle_error(self, message: str) -> None:
        self.status_var.set("エラーが発生しました")
        self.start_button.config(state=tk.NORMAL)
        messagebox.showerror("エラー", message)

    def _update_results(
        self, results: List[Tuple[str, float]], requested_count: int, total_valid: int
    ) -> None:
        self.tree.delete(*self.tree.get_children())

        for code, price in results:
            self.tree.insert("", tk.END, values=(code, f"{price:.2f}"))

        if results:
            status_message = f"{len(results)} 件の銘柄を表示中 (有効銘柄: {total_valid} 件)"
        else:
            status_message = "条件に一致する銘柄が見つかりませんでした。"

        self.status_var.set(status_message)
        self.start_button.config(state=tk.NORMAL)

        if len(results) < requested_count:
            messagebox.showinfo(
                "結果", f"条件に一致した銘柄は {len(results)} 件でした。"
            )


def run_cli(count: int, min_price: float, max_price: float) -> None:
    url = "https://nikkeiyosoku.com/stock/all/"

    try:
        codes = scrape_stock_codes(url)
        valid_codes = filter_valid_codes(codes)
    except Exception as exc:
        print(f"スクレイピングに失敗しました: {exc}", file=sys.stderr)
        sys.exit(1)

    if not valid_codes:
        print("有効な銘柄コードが見つかりませんでした。", file=sys.stderr)
        sys.exit(1)

    results = select_codes_by_price(valid_codes, count, min_price, max_price)

    if not results:
        print("条件に一致する銘柄が見つかりませんでした。")
        return

    print("抽出結果:")
    for code, price in results:
        print(f"  {code}: {price:.2f} 円")


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="銘柄コードスクレイパー")
    parser.add_argument("--count", type=int, default=30, help="抽出する銘柄数")
    parser.add_argument("--min-price", type=float, default=100, help="終値の下限")
    parser.add_argument("--max-price", type=float, default=500, help="終値の上限")
    parser.add_argument(
        "--cli",
        action="store_true",
        help="GUIの代わりにターミナル版を実行します",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_arguments()

    if args.count <= 0:
        raise SystemExit("--count には正の整数を指定してください。")
    if args.min_price > args.max_price:
        raise SystemExit("--min-price は --max-price 以下である必要があります。")

    if args.cli:
        run_cli(args.count, args.min_price, args.max_price)
        return

    try:
        root = tk.Tk()
    except tk.TclError:
        print("GUIの初期化に失敗したため、ターミナル版を起動します。", file=sys.stderr)
        run_cli(args.count, args.min_price, args.max_price)
        return

    app = StockScraperApp(root)
    app.count_var.set(str(args.count))
    app.min_price_var.set(str(args.min_price))
    app.max_price_var.set(str(args.max_price))
    root.mainloop()


if __name__ == "__main__":
    main()
