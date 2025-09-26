#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import yfinance as yf
import pandas as pd
from datetime import datetime
import os

def validate_ticker(ticker_code):
    """
    銘柄コードの妥当性をチェックする関数
    
    Parameters:
    ticker_code (str): 銘柄コード
    
    Returns:
    bool: 有効な銘柄コードの場合True
    """
    # 基本的な形式チェック
    if not ticker_code.isdigit():
        return False
    
    # 4桁の銘柄コードかチェック
    if len(ticker_code) != 4:
        return False
    
    # 一般的な東証銘柄コードの範囲チェック
    code_int = int(ticker_code)
    if code_int < 1000 or code_int > 9999:
        return False
    
    return True

def fetch_stock_data(ticker_code, start_date, end_date, market="TSE"):
    """
    指定された銘柄コードと期間で株価データを取得する関数
    
    Parameters:
    ticker_code (str): 銘柄コード（例: "7203"）
    start_date (str): 開始日（YYYY-MM-DD形式）
    end_date (str): 終了日（YYYY-MM-DD形式）
    market (str): 市場（"TSE"=東証、"US"=米国市場）
    
    Returns:
    pd.DataFrame: 株価データのDataFrame
    """
    # 東証の場合のみ銘柄コードの妥当性チェック
    if market == "TSE" and not validate_ticker(ticker_code):
        print(f"エラー: 無効な銘柄コードです: {ticker_code}")
        return None
    
    # 市場に応じてティッカーシンボルを設定
    if market == "TSE":
        # 東証の銘柄コードに.Tを付加
        ticker = ticker_code + ".T"
    else:
        # 米国市場の場合はそのまま使用
        ticker = ticker_code
    
    print(f"\n銘柄コード {ticker} のデータを取得中...")
    
    try:
        # yfinanceでデータ取得（複数の方法を試行）
        stock = yf.Ticker(ticker)
        df = None
        
        # 方法1: 通常の取得
        try:
            df = stock.history(start=start_date, end=end_date, auto_adjust=False, prepost=False)
        except:
            pass
        
        # 方法2: periodを使用した取得
        if df is None or df.empty:
            print(f"警告: 指定期間でデータが取得できませんでした。別の方法で再試行中...")
            try:
                # より長い期間で取得して後でフィルタリング
                df_long = stock.history(period="2y", auto_adjust=False, prepost=False)
                if not df_long.empty:
                    # 指定期間でフィルタリング
                    df = df_long.loc[start_date:end_date]
            except:
                pass
        
        # 方法3: downloadを使用した取得
        if df is None or df.empty:
            print(f"警告: 別の方法で再試行中...")
            try:
                df = yf.download(ticker, start=start_date, end=end_date, progress=False)
            except:
                pass
        
        if df is None or df.empty:
            print(f"警告: {ticker} のデータが取得できませんでした。")
            return None
        
        # カラム名を日本語に変更
        df = df.rename(columns={
            'Open': '始値',
            'High': '高値',
            'Low': '安値',
            'Close': '終値',
            'Volume': '出来高'
        })
        
        # 必要なカラムのみ選択
        df = df[['始値', '高値', '安値', '終値', '出来高']]
        
        # 20日移動平均線を計算
        df['20日移動平均'] = df['終値'].rolling(window=20, min_periods=1).mean()
        
        # 20日移動平均を小数点第2位まで丸める
        df['20日移動平均'] = df['20日移動平均'].round(2)
        
        # その他の価格データも小数点第2位まで丸める
        price_columns = ['始値', '高値', '安値', '終値']
        for col in price_columns:
            df[col] = df[col].round(2)
        
        # 出来高を整数に変換
        df['出来高'] = df['出来高'].astype(int)
        
        return df
        
    except Exception as e:
        print(f"エラー: データ取得中にエラーが発生しました: {e}")
        return None

def save_to_csv(df, ticker_code, start_date, end_date):
    """
    DataFrameをCSVファイルに保存する関数
    
    Parameters:
    df (pd.DataFrame): 保存するDataFrame
    ticker_code (str): 銘柄コード
    start_date (str): 開始日
    end_date (str): 終了日
    """
    # ファイル名を生成（銘柄コード_開始日_終了日.csv）
    start_date_formatted = start_date.replace('-', '')
    end_date_formatted = end_date.replace('-', '')
    filename = f"{ticker_code}_{start_date_formatted}_{end_date_formatted}.csv"
    
    # CSVに保存
    df.to_csv(filename, encoding='utf-8-sig')  # utf-8-sigでExcelでも文字化けしない
    
    print(f"\nデータを {filename} に保存しました。")
    print(f"保存場所: {os.path.abspath(filename)}")
    
    return filename

def validate_date(date_string):
    """
    日付の形式を検証する関数
    
    Parameters:
    date_string (str): 検証する日付文字列
    
    Returns:
    bool: 有効な日付形式の場合True
    """
    try:
        datetime.strptime(date_string, '%Y-%m-%d')
        return True
    except ValueError:
        return False

def main():
    """
    メイン処理
    """
    print("=" * 50)
    print("株価データ取得ツール (YFinance)")
    print("=" * 50)
    print("\n東証上場銘柄の株価データを取得してCSVファイルに出力します。")
    print("※銘柄コードには自動的に '.T' が付加されます。")
    print("-" * 50)
    
    while True:
        # 銘柄コード入力
        ticker_code = input("\n銘柄コードを入力してください（例: 7203=トヨタ、6758=ソニー、9984=ソフトバンク）: ").strip()
        
        if not ticker_code:
            print("エラー: 銘柄コードを入力してください。")
            continue
        
        # 銘柄コードの妥当性チェック
        if not validate_ticker(ticker_code):
            print("エラー: 銘柄コードは4桁の数字で入力してください（1000-9999）。")
            continue
        
        break
    
    while True:
        # 開始日入力
        start_date = input("開始日を入力してください（YYYY-MM-DD形式、例: 2024-01-01）: ").strip()
        
        if not validate_date(start_date):
            print("エラー: 日付は YYYY-MM-DD 形式で入力してください。")
            continue
        
        break
    
    while True:
        # 終了日入力
        end_date = input("終了日を入力してください（YYYY-MM-DD形式、例: 2024-12-31）: ").strip()
        
        if not validate_date(end_date):
            print("エラー: 日付は YYYY-MM-DD 形式で入力してください。")
            continue
        
        # 開始日と終了日の妥当性チェック
        if start_date > end_date:
            print("エラー: 終了日は開始日より後の日付を指定してください。")
            continue
        
        break
    
    # データ取得
    df = fetch_stock_data(ticker_code, start_date, end_date)
    
    if df is not None and not df.empty:
        # データのプレビュー表示
        print("\n取得したデータのプレビュー（最初の5行）:")
        print("-" * 80)
        print(df.head())
        print("-" * 80)
        print(f"\n合計 {len(df)} 日分のデータを取得しました。")
        
        # CSVに保存
        filename = save_to_csv(df, ticker_code, start_date, end_date)
        
        print("\n処理が完了しました！")
        print(f"CSVファイルには以下の情報が含まれています:")
        print("  - 日付（インデックス）")
        print("  - 始値")
        print("  - 高値")
        print("  - 安値")
        print("  - 終値")
        print("  - 出来高")
        print("  - 20日移動平均線")
        
    else:
        print("\nデータの取得に失敗しました。")
        print("以下の点を確認してください:")
        print("  - 銘柄コードが正しいか")
        print("  - 指定した期間にデータが存在するか")
        print("  - インターネット接続が正常か")

if __name__ == "__main__":
    main()
