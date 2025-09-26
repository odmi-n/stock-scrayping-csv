from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import threading
import time
from typing import Dict, Any, List, Tuple, Optional

# 既存のスクレイピング機能をインポート
from stock_code_scrayping import scrape_stock_codes, filter_valid_codes, select_codes_by_price

app = Flask(__name__)
CORS(app, origins=['http://localhost:3000'])  # Next.jsからのリクエストを許可

# グローバル変数でスクレイピングの状態を管理
scraping_status: Dict[str, Any] = {
    "is_running": False,
    "progress": 0,
    "status_message": "準備完了",
    "results": [],
    "error": None
}

@app.route('/')
def index():
    """メインページを表示"""
    return render_template('index.html')

@app.route('/api/scrape', methods=['POST'])
def start_scraping():
    """スクレイピングを開始するAPI"""
    global scraping_status
    
    if scraping_status["is_running"]:
        return jsonify({"error": "スクレイピングは既に実行中です"}), 400
    
    try:
        data = request.get_json()
        count = int(data.get('count', 30))
        min_price = float(data.get('min_price', 100))
        max_price = float(data.get('max_price', 500))
        
        if count <= 0:
            return jsonify({"error": "抽出銘柄数は正の整数を入力してください"}), 400
        
        if min_price > max_price:
            return jsonify({"error": "終値の下限は上限以下である必要があります"}), 400
            
    except (ValueError, TypeError):
        return jsonify({"error": "入力値が無効です"}), 400
    
    # バックグラウンドでスクレイピングを実行
    thread = threading.Thread(
        target=scrape_in_background,
        args=(count, min_price, max_price),
        daemon=True
    )
    thread.start()
    
    return jsonify({"message": "スクレイピングを開始しました"})

@app.route('/api/status')
def get_status():
    """スクレイピングの状態を取得するAPI"""
    return jsonify(scraping_status)

def scrape_in_background(count: int, min_price: float, max_price: float):
    """バックグラウンドでスクレイピングを実行"""
    global scraping_status
    
    scraping_status.update({
        "is_running": True,
        "progress": 0,
        "status_message": "銘柄コードを取得中...",
        "results": [],
        "error": None
    })
    
    url = "https://nikkeiyosoku.com/stock/all/"
    
    try:
        # 銘柄コードの取得
        scraping_status["status_message"] = "銘柄コードをスクレイピング中..."
        scraping_status["progress"] = 20
        
        codes = scrape_stock_codes(url)
        valid_codes = filter_valid_codes(codes)
        
        if not valid_codes:
            scraping_status.update({
                "is_running": False,
                "error": "有効な銘柄コードが見つかりませんでした",
                "status_message": "エラーが発生しました"
            })
            return
        
        scraping_status["progress"] = 50
        scraping_status["status_message"] = f"価格情報を取得中... (有効銘柄: {len(valid_codes)} 件)"
        
        # 価格条件に基づく銘柄の選択
        results = select_codes_by_price(valid_codes, count, min_price, max_price)
        
        scraping_status.update({
            "is_running": False,
            "progress": 100,
            "status_message": f"{len(results)} 件の銘柄を抽出完了 (有効銘柄: {len(valid_codes)} 件)",
            "results": [{"code": code, "price": price} for code, price in results],
            "error": None
        })
        
    except Exception as exc:
        scraping_status.update({
            "is_running": False,
            "error": f"スクレイピングに失敗しました: {str(exc)}",
            "status_message": "エラーが発生しました",
            "progress": 0
        })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
