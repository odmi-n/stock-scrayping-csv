import requests
from bs4 import BeautifulSoup
import re
import random

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



def main():
    url = "https://nikkeiyosoku.com/stock/all/"
    print("サイトから銘柄コードを取得中...")
    
    try:
        codes = scrape_stock_codes(url)
    except Exception as e:
        print("スクレイピング中にエラー:", e)
        return
    
    if not codes:
        print("銘柄コードが取得できませんでした。")
        return

    print("サイトから取得した銘柄数:", len(codes))
    
    # 有効なコードとして、1301以上の数値のみを対象にする
    valid_codes = filter_valid_codes(codes)
    print("有効な銘柄数（1301以上、REIT除外）:", len(valid_codes))
    
    try:
        count = int(input("抽出したい銘柄数を入力してください: "))
    except ValueError:
        print("数値を入力してください。")
        return
    
    if count > len(valid_codes):
        print("指定された抽出件数が、有効な銘柄数（{}）を超えています。".format(len(valid_codes)))
        return

    # 完全ランダム抽出（重複なし）
    chosen_codes = random.sample(valid_codes, count)
    
    # 例えば、銘柄コードを4桁で表示する場合はゼロパディング（英字がある場合は除く）
    chosen_codes_formatted = []
    for code in chosen_codes:
        if code.isdigit():
            chosen_codes_formatted.append(code.zfill(4))
        else:
            chosen_codes_formatted.append(code)
    
    print("\n抽出された銘柄コード一覧:")
    for code in chosen_codes_formatted:
        print(code)

if __name__ == '__main__':
    main()
