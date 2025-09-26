#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import threading
import os
import sys
from stock_data_fetcher import fetch_stock_data, save_to_csv

class StockDataGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("株価データ取得ツール")
        
        # ウィンドウサイズと位置の設定
        window_width = 800
        window_height = 700
        
        # 画面の中央に配置
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        
        self.root.geometry(f"{window_width}x{window_height}+{x}+{y}")
        self.root.minsize(750, 650)
        
        # スタイル設定
        self.setup_styles()
        
        # 変数の初期化
        self.ticker_var = tk.StringVar()
        self.start_date_var = tk.StringVar(value="2024-01-01")
        self.end_date_var = tk.StringVar(value="2024-12-31")
        self.progress_var = tk.DoubleVar()
        self.status_var = tk.StringVar(value="準備完了")
        
        # UI構築
        self.create_widgets()
        
    def setup_styles(self):
        """スタイルの設定"""
        style = ttk.Style()
        
        # macOS用のテーマ設定
        if sys.platform == 'darwin':
            style.theme_use('aqua')
        else:
            style.theme_use('clam')
        
        # カスタムスタイル
        style.configure('Title.TLabel', font=('Hiragino Sans', 20, 'bold'))
        style.configure('Subtitle.TLabel', font=('Hiragino Sans', 12))
        style.configure('Heading.TLabel', font=('Hiragino Sans', 11, 'bold'))
        style.configure('Info.TLabel', font=('Hiragino Sans', 10), foreground='#666666')
        style.configure('Large.TButton', font=('Hiragino Sans', 12), padding=(10, 8))
        style.configure('Status.TLabel', font=('Hiragino Sans', 11), foreground='#0066CC')
        
    def create_widgets(self):
        """ウィジェットの作成"""
        # メインコンテナ
        container = ttk.Frame(self.root)
        container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # タイトル部分
        self.create_header(container)
        
        # 入力部分
        self.create_input_section(container)
        
        # ボタン部分
        self.create_button_section(container)
        
        # プログレス部分
        self.create_progress_section(container)
        
        # 結果表示部分
        self.create_result_section(container)
        
    def create_header(self, parent):
        """ヘッダー部分の作成"""
        header_frame = ttk.Frame(parent)
        header_frame.pack(fill=tk.X, pady=(0, 20))
        
        title = ttk.Label(header_frame, text="株価データ取得ツール", style='Title.TLabel')
        title.pack()
        
        subtitle = ttk.Label(header_frame, 
                           text="東証上場銘柄の株価データを取得してCSVファイルに出力します",
                           style='Subtitle.TLabel')
        subtitle.pack(pady=(5, 0))
        
    def create_input_section(self, parent):
        """入力セクションの作成"""
        # 入力フレーム（枠線付き）
        input_container = ttk.LabelFrame(parent, text=" 入力項目 ", padding=20)
        input_container.pack(fill=tk.X, pady=(0, 20))
        
        # 銘柄コード行
        ticker_frame = ttk.Frame(input_container)
        ticker_frame.pack(fill=tk.X, pady=(0, 15))
        
        ttk.Label(ticker_frame, text="銘柄コード:", 
                 style='Heading.TLabel', width=12).pack(side=tk.LEFT)
        
        ticker_entry = ttk.Entry(ticker_frame, textvariable=self.ticker_var, 
                               width=10, font=('Hiragino Sans', 12))
        ticker_entry.pack(side=tk.LEFT, padx=(0, 15))
        
        ttk.Label(ticker_frame, 
                 text="例: 7203 (トヨタ)、6758 (ソニー)、9984 (ソフトバンク)",
                 style='Info.TLabel').pack(side=tk.LEFT)
        
        # 開始日行
        start_frame = ttk.Frame(input_container)
        start_frame.pack(fill=tk.X, pady=(0, 15))
        
        ttk.Label(start_frame, text="開始日:", 
                 style='Heading.TLabel', width=12).pack(side=tk.LEFT)
        
        start_entry = ttk.Entry(start_frame, textvariable=self.start_date_var,
                              width=15, font=('Hiragino Sans', 12))
        start_entry.pack(side=tk.LEFT, padx=(0, 15))
        
        ttk.Label(start_frame, text="YYYY-MM-DD形式", 
                 style='Info.TLabel').pack(side=tk.LEFT)
        
        # 終了日行
        end_frame = ttk.Frame(input_container)
        end_frame.pack(fill=tk.X)
        
        ttk.Label(end_frame, text="終了日:", 
                 style='Heading.TLabel', width=12).pack(side=tk.LEFT)
        
        end_entry = ttk.Entry(end_frame, textvariable=self.end_date_var,
                            width=15, font=('Hiragino Sans', 12))
        end_entry.pack(side=tk.LEFT, padx=(0, 15))
        
        ttk.Label(end_frame, text="YYYY-MM-DD形式", 
                 style='Info.TLabel').pack(side=tk.LEFT)
        
    def create_button_section(self, parent):
        """ボタンセクションの作成"""
        button_frame = ttk.Frame(parent)
        button_frame.pack(pady=(0, 20))
        
        self.fetch_button = ttk.Button(button_frame, 
                                      text="データ取得開始",
                                      command=self.start_fetch_data,
                                      style='Large.TButton')
        self.fetch_button.pack(side=tk.LEFT, padx=5)
        
        clear_button = ttk.Button(button_frame,
                                text="入力クリア",
                                command=self.clear_inputs,
                                style='Large.TButton')
        clear_button.pack(side=tk.LEFT, padx=5)
        
    def create_progress_section(self, parent):
        """プログレスセクションの作成"""
        progress_container = ttk.LabelFrame(parent, text=" 進行状況 ", padding=15)
        progress_container.pack(fill=tk.X, pady=(0, 20))
        
        # プログレスバー
        self.progress_bar = ttk.Progressbar(progress_container,
                                           variable=self.progress_var,
                                           maximum=100,
                                           mode='determinate')
        self.progress_bar.pack(fill=tk.X, pady=(0, 10))
        
        # ステータスラベル
        status_label = ttk.Label(progress_container,
                               textvariable=self.status_var,
                               style='Status.TLabel')
        status_label.pack(anchor=tk.W)
        
    def create_result_section(self, parent):
        """結果表示セクションの作成"""
        result_container = ttk.LabelFrame(parent, text=" 取得結果 ", padding=15)
        result_container.pack(fill=tk.BOTH, expand=True)
        
        # テキストウィジェットとスクロールバー
        text_frame = ttk.Frame(result_container)
        text_frame.pack(fill=tk.BOTH, expand=True)
        
        # スクロールバー
        v_scrollbar = ttk.Scrollbar(text_frame, orient=tk.VERTICAL)
        v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        h_scrollbar = ttk.Scrollbar(text_frame, orient=tk.HORIZONTAL)
        h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # テキストエリア
        self.result_text = tk.Text(text_frame,
                                  wrap=tk.NONE,
                                  font=('Monaco', 11),
                                  bg='#F5F5F5',
                                  fg='#333333',
                                  yscrollcommand=v_scrollbar.set,
                                  xscrollcommand=h_scrollbar.set)
        self.result_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        v_scrollbar.config(command=self.result_text.yview)
        h_scrollbar.config(command=self.result_text.xview)
        
    def validate_inputs(self):
        """入力値の検証"""
        ticker = self.ticker_var.get().strip()
        start_date = self.start_date_var.get().strip()
        end_date = self.end_date_var.get().strip()
        
        # 銘柄コードの検証
        if not ticker:
            messagebox.showerror("入力エラー", "銘柄コードを入力してください。")
            return False
        
        if not ticker.isdigit() or len(ticker) != 4:
            messagebox.showerror("入力エラー", "銘柄コードは4桁の数字で入力してください。")
            return False
        
        # 日付形式の検証
        try:
            datetime.strptime(start_date, '%Y-%m-%d')
            datetime.strptime(end_date, '%Y-%m-%d')
        except ValueError:
            messagebox.showerror("入力エラー", "日付はYYYY-MM-DD形式で入力してください。")
            return False
        
        # 日付の論理的検証
        if start_date > end_date:
            messagebox.showerror("入力エラー", "終了日は開始日より後の日付を指定してください。")
            return False
        
        return True
    
    def clear_inputs(self):
        """入力フィールドをクリア"""
        self.ticker_var.set("")
        self.start_date_var.set("2024-01-01")
        self.end_date_var.set("2024-12-31")
        self.result_text.delete(1.0, tk.END)
        self.progress_var.set(0)
        self.status_var.set("準備完了")
    
    def log_message(self, message, newline=True):
        """結果表示エリアにメッセージを追加"""
        if newline:
            message += "\n"
        self.result_text.insert(tk.END, message)
        self.result_text.see(tk.END)
        self.root.update_idletasks()
    
    def start_fetch_data(self):
        """データ取得を開始（別スレッドで実行）"""
        if not self.validate_inputs():
            return
        
        # UIを無効化
        self.fetch_button.config(state='disabled')
        self.result_text.delete(1.0, tk.END)
        self.progress_var.set(0)
        self.status_var.set("データ取得中...")
        
        # 別スレッドでデータ取得を実行
        thread = threading.Thread(target=self.fetch_data_thread)
        thread.daemon = True
        thread.start()
    
    def fetch_data_thread(self):
        """データ取得のメイン処理（別スレッドで実行）"""
        try:
            ticker = self.ticker_var.get().strip()
            start_date = self.start_date_var.get().strip()
            end_date = self.end_date_var.get().strip()
            
            self.log_message(f"銘柄コード: {ticker}")
            self.log_message(f"期間: {start_date} ～ {end_date}")
            self.log_message("=" * 60)
            self.log_message("")
            
            # プログレスバー更新
            self.progress_var.set(20)
            self.status_var.set("YFinanceからデータを取得中...")
            
            # データ取得
            self.log_message("📡 株価データを取得中...")
            df = fetch_stock_data(ticker, start_date, end_date)
            
            self.progress_var.set(60)
            
            if df is not None and not df.empty:
                self.log_message(f"✅ データ取得成功！ ({len(df)} 日分のデータ)")
                self.log_message("")
                
                # データのプレビュー表示
                self.log_message("【データプレビュー】最初の5行:")
                self.log_message("-" * 60)
                
                # データフレームを整形して表示
                preview_str = df.head().to_string()
                for line in preview_str.split('\n'):
                    self.log_message(line)
                
                self.log_message("-" * 60)
                self.log_message("")
                
                self.progress_var.set(80)
                self.status_var.set("CSVファイル作成中...")
                
                # CSVファイル保存
                filename = save_to_csv(df, ticker, start_date, end_date)
                
                self.progress_var.set(100)
                self.status_var.set("✅ 完了しました！")
                
                self.log_message("【CSVファイル作成完了】")
                self.log_message(f"📁 ファイル名: {filename}")
                self.log_message(f"📍 保存場所: {os.path.abspath(filename)}")
                self.log_message("")
                self.log_message("【CSVファイルに含まれるデータ】")
                self.log_message("  ✓ 日付（インデックス）")
                self.log_message("  ✓ 始値")
                self.log_message("  ✓ 高値")
                self.log_message("  ✓ 安値")
                self.log_message("  ✓ 終値")
                self.log_message("  ✓ 出来高")
                self.log_message("  ✓ 20日移動平均線")
                self.log_message("")
                self.log_message("=" * 60)
                self.log_message("処理が正常に完了しました！")
                
                # 成功メッセージ
                self.root.after(0, lambda: messagebox.showinfo("完了", 
                    f"データ取得が完了しました！\n\n"
                    f"ファイル名: {filename}\n"
                    f"取得データ: {len(df)} 日分\n\n"
                    f"CSVファイルが保存されました。"))
                
            else:
                self.progress_var.set(0)
                self.status_var.set("❌ エラーが発生しました")
                
                self.log_message("❌ データ取得に失敗しました")
                self.log_message("")
                self.log_message("【確認事項】")
                self.log_message("  1. 銘柄コードが正しいか確認してください")
                self.log_message("  2. 指定した期間に取引データが存在するか確認してください")
                self.log_message("  3. インターネット接続が正常か確認してください")
                self.log_message("  4. 銘柄が上場廃止になっていないか確認してください")
                self.log_message("")
                self.log_message("※土日祝日は取引がないため、データは存在しません")
                
                self.root.after(0, lambda: messagebox.showerror("エラー", 
                    "データ取得に失敗しました。\n\n"
                    "入力内容とネットワーク接続を確認してください。"))
                
        except Exception as e:
            self.progress_var.set(0)
            self.status_var.set("❌ 予期しないエラー")
            
            error_msg = f"予期しないエラーが発生しました:\n{str(e)}"
            self.log_message(f"❌ {error_msg}")
            
            self.root.after(0, lambda: messagebox.showerror("エラー", error_msg))
        
        finally:
            # UIを再有効化
            self.root.after(0, lambda: self.fetch_button.config(state='normal'))

def main():
    """メイン関数"""
    root = tk.Tk()
    
    # macOSの場合、Retinaディスプレイ対応
    if sys.platform == 'darwin':
        root.tk.call('tk', 'scaling', 1.0)
    
    app = StockDataGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()