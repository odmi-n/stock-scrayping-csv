from flask import Flask, request, jsonify, Response
import os
import json
import tempfile
from flask_cors import CORS

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})

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

@app.route('/api/status', methods=['GET', 'OPTIONS'])
def status():
    """ステータス確認エンドポイント"""
    if request.method == 'OPTIONS':
        return '', 200, {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'GET, OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type'
        }
    
    return jsonify(get_status())

@app.route('/api/scrape', methods=['POST', 'OPTIONS'])
def scrape():
    """スクレイピング開始エンドポイント"""
    # 相対インポートではなく、絶対インポート
    import sys
    import os
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    from scrape import scrape_in_background
    
    if request.method == 'OPTIONS':
        return '', 200, {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'POST, OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type'
        }
    
    current_status = get_status()
    if current_status["is_running"]:
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
    import threading
    thread = threading.Thread(
        target=scrape_in_background,
        args=(count, min_price, max_price),
        daemon=True
    )
    thread.start()
    
    return jsonify({"message": "スクレイピングを開始しました"})

# Vercel用のエントリーポイント
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def catch_all(path):
    return jsonify({"message": "Welcome to Stock Scraper API", "status": "online"})

# Vercelのサーバレス関数用ハンドラー
def handler(request):
    """Vercel Serverless Function handler"""
    with app.test_request_context(
        path=request.get('path', '/'),
        method=request.get('method', 'GET'),
        headers=request.get('headers', {}),
        data=request.get('body', b'')
    ):
        try:
            response = app.full_dispatch_request()
            return {
                'statusCode': response.status_code,
                'headers': dict(response.headers),
                'body': response.get_data().decode('utf-8')
            }
        except Exception as e:
            return {
                'statusCode': 500,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({"error": str(e)})
            }
