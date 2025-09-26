#!/bin/bash

# Next.js + Flask 株価スクレイピングアプリケーション起動スクリプト

echo "🚀 Next.js + Flask 株価スクレイピングアプリケーションを起動しています..."

# 仮想環境の確認とアクティベート（Flask用）
if [ -d "test_env" ]; then
    echo "📦 Python仮想環境をアクティベートしています..."
    source test_env/bin/activate
else
    echo "⚠️  Python仮想環境が見つかりません。新しい仮想環境を作成します..."
    python3 -m venv test_env
    source test_env/bin/activate
    echo "📥 Python依存関係をインストールしています..."
    pip install -r requirements.txt
fi

# Python依存関係の確認とインストール
echo "🔍 Python依存関係を確認しています..."
pip install -r requirements.txt

# Next.jsディレクトリに移動してNode.js依存関係を確認
echo "📦 Next.js依存関係を確認しています..."
cd stock-scraper-nextjs
npm install

echo ""
echo "🎯 アプリケーションを起動しています..."
echo "📋 Flaskバックエンド: http://localhost:5000"
echo "🌐 Next.jsフロントエンド: http://localhost:3000"
echo "🛑 アプリケーションを停止するには両方のターミナルでCtrl+Cを押してください"
echo ""

# バックグラウンドでFlaskサーバーを起動
echo "🐍 Flaskバックエンドを起動中..."
cd ..
python stock_web_app.py &
FLASK_PID=$!

# 少し待ってからNext.jsを起動
sleep 3

echo "⚛️  Next.jsフロントエンドを起動中..."
cd stock-scraper-nextjs
npm run dev &
NEXTJS_PID=$!

# 両方のプロセスを待機
wait $FLASK_PID $NEXTJS_PID
