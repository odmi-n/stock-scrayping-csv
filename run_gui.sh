#!/bin/bash
# 株価データ取得ツール（GUI版）起動スクリプト

echo "株価データ取得ツール（GUI版）を起動中..."
echo "仮想環境をアクティベート中..."

# スクリプトがあるディレクトリに移動
cd "$(dirname "$0")"

# 仮想環境をアクティベート
source .venv/bin/activate

# GUIアプリケーション実行
echo "GUIアプリケーションを起動します..."
python stock_data_gui.py
