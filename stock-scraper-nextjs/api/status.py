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

def handler(request):
    """Vercel Serverless Function handler"""
    if request.method == 'GET':
        status = get_status()
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'GET, OPTIONS',
                'Access-Control-Allow-Headers': 'Content-Type'
            },
            'body': json.dumps(status)
        }
    
    elif request.method == 'OPTIONS':
        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'GET, OPTIONS',
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