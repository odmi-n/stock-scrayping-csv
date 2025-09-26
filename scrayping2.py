import requests
from bs4 import BeautifulSoup
import re
import random
import yfinance as yf
import pandas as pd
import time

def scrape_stock_codes(url):
    """
    指定されたURLから東証の全銘柄コードをスクレイピングする。
    ページ内の <a> タグ href 属性から '/stock/数字' にマッチする部分を抽出する。
    """
    response = requests.get(url)
    if response.status_code != 200:
        raise Exception("ページの取得に失敗しました。")
    
    soup = BeautifulSoup(response.text, 'html.parser')
    codes = set()
    
    # すべてのリンクから、'/stock/数字' を抽出
    for a in soup.find_all('a', href=True):
        match = re.search(r'/stock/(\d+)', a['href'])
        if match:
            codes.add(match.group(1).strip())
    
    return list(codes)

def filter_valid_codes(codes):
    """
    取得した銘柄コードのうち、数値として変換可能かつ 1301 以上のもののみを返す。
    ※これによりETFやブル等、意図しないコードを除外する。
    """
    valid = []
    for code in codes:
        if code.isdigit():
            if int(code) >= 1301:
                valid.append(code)
    return valid

def get_previous_closes_batch(tickers, batch_size=100, sleep_time=1):
    """
    複数のティッカーシンボルに対して、バッチごとに yfinance から
    前日の終値（Close）を取得する。
    
    ・tickers: 例 ["7203.T", "6758.T", ...]
    ・batch_size: 一度に処理するティッカー数（デフォルト 100）
    ・sleep_time: バッチ間の待機秒数（サーバ負荷軽減用）
    
    戻り値:
      {ticker: previous_close, ... } の辞書
    """
    previous_closes = {}
    
    for i in range(0, len(tickers), batch_size):
        batch = tickers[i:i+batch_size]
        try:
            # threads=False でスレッド数を制限
            data = yf.download(tickers=batch, period="2d", interval="1d", progress=False, threads=False)
        except Exception as e:
            print(f"バッチ {i}～{i+batch_size} のダウンロードでエラー: {e}")
            continue

        if data.empty:
            continue

        # 複数ティッカーの場合、カラムはMultiIndexになる
        if isinstance(data.columns, pd.MultiIndex):
            for ticker in batch:
                try:
                    if ticker in data['Close'].columns:
                        ticker_data = data['Close'][ticker]
                        if not ticker_data.empty:
                            previous_closes[ticker] = ticker_data.iloc[0]
                except Exception as e:
                    print(f"{ticker} の処理中にエラー: {e}")
                    continue
        else:
            # ティッカーが1つだけの場合
            ticker = batch[0]
            if not data.empty:
                previous_closes[ticker] = data['Close'].iloc[0]
        time.sleep(sleep_time)
    
    return previous_closes

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
    print("有効な銘柄数（1301以上）:", len(valid_codes))
    
    # yfinance用に、各コードに末尾 ".T" を付加する
    tickers = [code + ".T" for code in valid_codes]
    
    try:
        lower = float(input("抽出する前日の終値の下限を入力してください: "))
        upper = float(input("抽出する前日の終値の上限を入力してください: "))
        count = int(input("抽出したい銘柄数を入力してください: "))
    except ValueError:
        print("数値を入力してください。")
        return
    
    print("yfinanceで前日の終値を取得中...")
    previous_closes = get_previous_closes_batch(tickers, batch_size=100, sleep_time=1)
    
    if not previous_closes:
        print("yfinanceから価格情報を取得できませんでした。")
        return
    
    # 前日の終値が指定範囲内のティッカーを抽出
    filtered = []
    for ticker, close in previous_closes.items():
        if lower <= close <= upper:
            filtered.append((ticker, close))
    
    if not filtered:
        print("指定された価格範囲に合致する銘柄は存在しません。")
        return
    
    if count > len(filtered):
        print("指定された抽出件数が、フィルタリングされた銘柄数（{}）を超えています。".format(len(filtered)))
        return
    
    chosen = random.sample(filtered, count)
    
    print("\n抽出された銘柄一覧 (Ticker : 前日の終値):")
    for ticker, close in chosen:
        print(f"{ticker}: {close}")

if __name__ == '__main__':
    main()
