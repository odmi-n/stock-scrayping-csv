from http.server import BaseHTTPRequestHandler
import json
import os
import tempfile

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

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        status = get_status()
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(status).encode())
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()