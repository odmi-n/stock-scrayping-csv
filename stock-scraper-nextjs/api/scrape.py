from http.server import BaseHTTPRequestHandler
import json
import threading
import time
import os
import tempfile
from typing import Dict, Any, List, Tuple, Optional
import requests
from bs4 import BeautifulSoup
import re
import random
import yfinance as yf

def get_status():
    """ファイルシステムから状態を取得"""
    try:
        status_file = os.path.join(tempfile.gettempdir(), 'scraping_status.json')
        if os.path.exists(status_file):
            with open(status_file, 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception:
        pass
    
    # デフォルト状態
    return {
        "is_running": False,
        "progress": 0,
        "status_message": "準備完了",
        "results": [],
        "error": None
    }

def save_status(status):
    """ファイルシステムに状態を保存"""
    try:
        status_file = os.path.join(tempfile.gettempdir(), 'scraping_status.json')
        with open(status_file, 'w', encoding='utf-8') as f:
            json.dump(status, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"Failed to save status: {e}")

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

def scrape_in_background(count: int, min_price: float, max_price: float):
    """バックグラウンドでスクレイピングを実行"""
    status = {
        "is_running": True,
        "progress": 0,
        "status_message": "銘柄コードを取得中...",
        "results": [],
        "error": None
    }
    save_status(status)
    
    url = "https://nikkeiyosoku.com/stock/all/"
    
    try:
        # 銘柄コードの取得
        status["status_message"] = "銘柄コードをスクレイピング中..."
        status["progress"] = 20
        save_status(status)
        
        codes = scrape_stock_codes(url)
        valid_codes = filter_valid_codes(codes)
        
        if not valid_codes:
            status.update({
                "is_running": False,
                "error": "有効な銘柄コードが見つかりませんでした",
                "status_message": "エラーが発生しました"
            })
            save_status(status)
            return
        
        status["progress"] = 50
        status["status_message"] = f"価格情報を取得中... (有効銘柄: {len(valid_codes)} 件)"
        save_status(status)
        
        # 価格条件に基づく銘柄の選択
        results = select_codes_by_price(valid_codes, count, min_price, max_price)
        
        # 結果を安全にJSONシリアライズできる形式に変換
        json_results = []
        for code, price in results:
            try:
                # 銘柄コードと価格を文字列として安全に処理
                safe_code = str(code) if code else ""
                safe_price = float(price) if price is not None else 0.0
                json_results.append({"code": safe_code, "price": safe_price})
            except (ValueError, TypeError) as e:
                print(f"Warning: Failed to process result {code}, {price}: {e}")
                continue
        
        status.update({
            "is_running": False,
            "progress": 100,
            "status_message": f"{len(json_results)} 件の銘柄を抽出完了 (有効銘柄: {len(valid_codes)} 件)",
            "results": json_results,
            "error": None
        })
        save_status(status)
        
    except Exception as exc:
        status.update({
            "is_running": False,
            "error": f"スクレイピングに失敗しました: {str(exc)}",
            "status_message": "エラーが発生しました",
            "progress": 0
        })
        save_status(status)

def handler(request):
    """Vercel Serverless Function handler"""
    if request.method == 'POST':
        current_status = get_status()
        
        if current_status["is_running"]:
            return {
                'statusCode': 400,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({"error": "スクレイピングは既に実行中です"})
            }
        
        try:
            body = json.loads(request.body.decode('utf-8')) if hasattr(request, 'body') else request.json
            count = int(body.get('count', 30))
            min_price = float(body.get('min_price', 100))
            max_price = float(body.get('max_price', 500))
            
            if count <= 0:
                return {
                    'statusCode': 400,
                    'headers': {'Content-Type': 'application/json'},
                    'body': json.dumps({"error": "抽出銘柄数は正の整数を入力してください"})
                }
            
            if min_price > max_price:
                return {
                    'statusCode': 400,
                    'headers': {'Content-Type': 'application/json'},
                    'body': json.dumps({"error": "終値の下限は上限以下である必要があります"})
                }
                
        except (ValueError, TypeError):
            return {
                'statusCode': 400,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({"error": "入力値が無効です"})
            }
        
        # バックグラウンドでスクレイピングを実行
        thread = threading.Thread(
            target=scrape_in_background,
            args=(count, min_price, max_price),
            daemon=True
        )
        thread.start()
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'POST, OPTIONS',
                'Access-Control-Allow-Headers': 'Content-Type'
            },
            'body': json.dumps({"message": "スクレイピングを開始しました"})
        }
    
    elif request.method == 'OPTIONS':
        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'POST, OPTIONS',
                'Access-Control-Allow-Headers': 'Content-Type'
            },
            'body': ''
        }
    
    else:
        return {
            'statusCode': 405,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({"error": "Method not allowed"})
        }