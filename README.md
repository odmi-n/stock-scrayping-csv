# 株価データ取得ツール

YFinanceを使用して東証上場銘柄の株価データを取得し、CSVファイルに出力するPythonアプリケーションです。

## 機能

- 東証上場銘柄の株価データ取得（自動的に`.T`サフィックスを付加）
- 指定期間での高値・安値・出来高・始値・終値の取得
- 20日移動平均線の自動計算
- CSVファイルへの出力
- **GUI版、CUI版、Webアプリ版、Next.js Liquid Glass版の4つのインターフェース**

## 必要なパッケージ

```bash
pip install -r requirements.txt
```

## 使用方法

### 📊 銘柄コードスクレイパー（`stock_code_scrayping.py`）

東証銘柄一覧をスクレイピングし、yfinanceの終値で絞り込みます。GUI、ターミナル、Webアプリ、Next.js Liquid Glassの4つのインターフェースが利用可能です。

#### 🌐 Webアプリ版を起動する（推奨）

```bash
./run_web_app.sh
```

または手動で：
```bash
source test_env/bin/activate
python stock_web_app.py
```

ブラウザで `http://localhost:5000` にアクセスしてください。

#### ✨ Next.js Liquid Glass版を起動する（最新・推奨）

```bash
./run_nextjs_app.sh
```

または手動で：
```bash
# バックエンド起動（ターミナル1）
source test_env/bin/activate
python stock_web_app.py

# フロントエンド起動（ターミナル2）
cd stock-scraper-nextjs
npm install
npm run dev
```

フロントエンド: `http://localhost:3000` / バックエンド: `http://localhost:5000`

**特徴:**
- 🎨 Apple風Liquid Glassデザイン
- 📱 完全レスポンシブ対応
- ⚡ リアルタイム進行状況表示
- 🌊 美しいアニメーション効果

#### 🖥️ GUIを起動する

```bash
python stock_code_scrayping.py
```

GUIを利用する場合はディスプレイ環境が必要です。`--count` / `--min-price` / `--max-price` を同時に指定すると、起動時のフォームにも反映されます。

#### 💻 ターミナル版を起動する

```bash
python stock_code_scrayping.py --cli --count 30 --min-price 100 --max-price 500
```

GUIが利用できない環境（例：SSH接続のサーバー）では自動的にターミナル版に切り替わります。ターミナル版では抽出結果が標準出力に一覧表示されます。

### 🖥️ GUI版（推奨）

**方法1: 起動スクリプトを使用**
```bash
./run_gui.sh
```

**方法2: 手動実行**
```bash
source .venv/bin/activate
python stock_data_gui.py
```

GUI版では以下の機能が利用できます：
- 直感的な入力フォーム
- リアルタイムの進行状況表示
- データプレビュー表示
- エラーハンドリングとメッセージ表示

### 💻 CUI版（ターミナル版）

```bash
source .venv/bin/activate
python stock_data_fetcher.py
```

## 入力項目

以下の情報を入力してください：
- **銘柄コード**: 4桁の数字（例：7203=トヨタ、6758=ソニー、9984=ソフトバンク）
- **開始日**: YYYY-MM-DD形式
- **終了日**: YYYY-MM-DD形式

## 出力ファイル

CSVファイルは以下の形式で作成されます：
- ファイル名：`{銘柄コード}_{開始日}_{終了日}.csv`
- 内容：
  - 日付
  - 始値
  - 高値
  - 安値
  - 終値
  - 出来高
  - 20日移動平均線

## 使用例

```bash
銘柄コード: 6758  # ソニー
開始日: 2024-08-01
終了日: 2024-08-31
```

出力ファイル：`6758_20240801_20240831.csv`

## 注意事項

- インターネット接続が必要です
- 土日祝日や取引停止日のデータは含まれません
- 20日移動平均線は取得したデータの期間内で計算されます
- 銘柄コードは東証に上場している4桁の数字を入力してください

## トラブルシューティング

データが取得できない場合：
1. 銘柄コードが正しいか確認
2. 指定した期間にデータが存在するか確認
3. インターネット接続を確認
4. 銘柄が上場廃止になっていないか確認
