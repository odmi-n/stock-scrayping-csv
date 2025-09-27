import json

# スクレイピング状態を共有するため、scrape.pyからインポート
try:
    from .scrape import scraping_status
except ImportError:
    # フォールバック用のデフォルト状態
    scraping_status = {
        "is_running": False,
        "progress": 0,
        "status_message": "準備完了",
        "results": [],
        "error": None
    }

def handler(request):
    """Vercelのサーバレス関数でスクレイピング状態を取得"""
    if request.method == 'GET':
        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps(scraping_status)
        }
    else:
        return {
            'statusCode': 405,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({"error": "Method not allowed"})
        }
