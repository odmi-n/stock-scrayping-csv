import requests
from bs4 import BeautifulSoup
import re
import random

def scrape_stock_codes(url):
    """
    指定されたURLから銘柄コードをスクレイピングする関数。
    
    この例では、ページ内のすべての<a>タグのhref属性から、
    パターン '/stock/数字' にマッチする部分（銘柄コード）を抽出しています。
    """
    response = requests.get(url)
    if response.status_code != 200:
        raise Exception("ページの取得に失敗しました。")
        
    soup = BeautifulSoup(response.text, 'html.parser')
    codes = set()  # ユニークな銘柄コードを保存するため集合を使用
    
    # すべてのリンクを走査して、href属性中に銘柄コードらしき数字があれば抽出
    for a in soup.find_all('a', href=True):
        match = re.search(r'/stock/(\d+)', a['href'])
        if match:
            codes.add(match.group(1))
            
    return list(codes)

def filter_by_boundaries(codes, lower, upper):
    """
    銘柄コード（文字列リスト）を、指定された下限・上限の整数値の範囲でフィルタリング
    """
    filtered = [code for code in codes if lower <= int(code) <= upper]
    return filtered

def main():
    url = "https://nikkeiyosoku.com/stock/all/"
    print("サイトから銘柄情報を取得中...")
    
    try:
        stock_codes = scrape_stock_codes(url)
    except Exception as e:
        print("スクレイピング中にエラーが発生しました:", e)
        return
    
    if not stock_codes:
        print("銘柄が見つかりませんでした。")
        return

    # 数字順にソート（整数として比較）
    stock_codes = sorted(stock_codes, key=lambda x: int(x))
    print("取得した銘柄数:", len(stock_codes))
    
    try:
        lower = int(input("抽出する銘柄コードの下限を入力してください: "))
        upper = int(input("抽出する銘柄コードの上限を入力してください: "))
        count = int(input("抽出したい銘柄数を入力してください: "))
    except ValueError:
        print("数値を入力してください。")
        return

    filtered_codes = filter_by_boundaries(stock_codes, lower, upper)
    
    if not filtered_codes:
        print("指定された範囲内の銘柄が存在しません。")
        return
    
    if count > len(filtered_codes):
         print("指定された抽出件数が、フィルタされた銘柄数（{}）を超えています。".format(len(filtered_codes)))
         return

    # ランダム抽出（重複なし）
    chosen_codes = random.sample(filtered_codes, count)
    
    # 例えば、銘柄コードを4桁で表示する場合はゼロパディング
    chosen_codes_formatted = [code.zfill(4) for code in chosen_codes]
    
    print("\n抽出された銘柄コード一覧:")
    for code in chosen_codes_formatted:
        print(code)

if __name__ == '__main__':
    main()
