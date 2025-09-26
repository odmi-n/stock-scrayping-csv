#!/bin/bash

# 株価スクレイピングWebアプリケーション起動スクリプト

echo "🚀 株価スクレイピングWebアプリケーションを起動しています..."

# 仮想環境の確認とアクティベート
if [ -d "test_env" ]; then
    echo "📦 仮想環境をアクティベートしています..."
    source test_env/bin/activate
else
    echo "⚠️  仮想環境が見つかりません。新しい仮想環境を作成します..."
    python3 -m venv test_env
    source test_env/bin/activate
    echo "📥 依存関係をインストールしています..."
    pip install -r requirements.txt
fi

# 依存関係の確認とインストール
echo "🔍 依存関係を確認しています..."
pip install -r requirements.txt

# Webアプリケーションの起動
echo "🌐 Webアプリケーションを起動しています..."
echo "📋 ブラウザで http://localhost:5000 にアクセスしてください"
echo "🛑 アプリケーションを停止するには Ctrl+C を押してください"
echo ""

python stock_web_app.py

