import requests
from bs4 import BeautifulSoup
import re
import random
from typing import List, Optional, Tuple

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
    if not code:
        return None
    
    # 銘柄コードから数字部分を抽出して.Tを付加
    numeric_part = re.match(r'(\d+)', code)
    if not numeric_part:
        return None
    
    ticker = f"{numeric_part.group(1)}.T"
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
            # 数字部分を4桁でゼロパディング、英字部分があれば保持
            numeric_part = re.match(r'(\d+)', code)
            if numeric_part:
                base_code = numeric_part.group(1).zfill(4)
                # 元のコードに英字部分があれば付加
                alpha_part = code[len(numeric_part.group(1)):]
                display_code = base_code + alpha_part
            else:
                display_code = code
            filtered.append((display_code, close_price))

    return filtered


