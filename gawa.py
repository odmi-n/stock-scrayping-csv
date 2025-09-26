import tkinter as tk
from tkinter import ttk
from tkinter import messagebox

class ExtractionApp:
    """データ抽出設定UIのメインアプリケーションクラス"""
    def __init__(self, root):
        self.root = root
        self.root.title("抽出設定画面")
        self.root.geometry("320x220")
        self.root.resizable(False, False)

        main_frame = ttk.Frame(self.root, padding="10 10 10 10")
        main_frame.grid(row=0, column=0, sticky=('n', 'w', 'e', 's'))
        
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        
        main_frame.columnconfigure(0, weight=1)

        self._create_widgets(main_frame)

    def _create_widgets(self, parent_frame):
        """UIウィジェットを作成し、配置する"""
        # --- コンテナフレームの作成 ---
        price_frame = ttk.LabelFrame(parent_frame, text="価格", padding="10")
        price_frame.grid(row=0, column=0, sticky=('ew'), padx=5, pady=5)
        
        count_frame = ttk.LabelFrame(parent_frame, text="抽出個数", padding="10")
        count_frame.grid(row=1, column=0, sticky=('ew'), padx=5, pady=5)

        action_frame = ttk.Frame(parent_frame, padding="10")
        action_frame.grid(row=2, column=0, sticky=('ew'), padx=5, pady=5)

        # --- 価格範囲ウィジェット ---
        self.price_min_entry = ttk.Entry(price_frame, width=10)
        self.price_min_entry.grid(row=0, column=0, sticky=('ew'), padx=(0, 5))

        price_tilde_label = ttk.Label(price_frame, text="円  ～")
        price_tilde_label.grid(row=0, column=1, padx=5)

        self.price_max_entry = ttk.Entry(price_frame, width=10)
        self.price_max_entry.grid(row=0, column=2, sticky=('ew'), padx=(5, 0))

        price_yen_label = ttk.Label(price_frame, text="円")
        price_yen_label.grid(row=0, column=3, padx=5)
        
        price_frame.columnconfigure(0, weight=1)
        price_frame.columnconfigure(2, weight=1)

        # --- 抽出個数ウィジェット ---
        self.count_option_var = tk.IntVar(value=1)

        self.count_specific_radio = ttk.Radiobutton(
            count_frame, text="", variable=self.count_option_var, 
            value=1, command=self._on_count_option_change)
        self.count_specific_radio.grid(row=0, column=0, sticky='w')

        self.count_specific_entry = ttk.Entry(count_frame, width=8)
        self.count_specific_entry.grid(row=0, column=1, sticky='w')

        count_unit_label = ttk.Label(count_frame, text="個")
        count_unit_label.grid(row=0, column=2, sticky='w', padx=5)

        self.count_all_radio = ttk.Radiobutton(
            count_frame, text="全て抽出する", variable=self.count_option_var,
            value=2, command=self._on_count_option_change)
        self.count_all_radio.grid(row=1, column=0, columnspan=3, sticky='w', pady=(5,0))

        self._on_count_option_change()

        # --- アクションボタン ---
        self.start_button = ttk.Button(action_frame, text="抽出開始", command=self.start_extraction)
        self.start_button.pack()

    def _on_count_option_change(self):
        """ラジオボタンの選択に応じて個数入力フィールドの状態を切り替える"""
        if self.count_option_var.get() == 1:
            self.count_specific_entry.config(state='normal')
        else:
            self.count_specific_entry.config(state='disabled')

    def start_extraction(self):
        """抽出開始ボタンが押されたときの処理"""
        print("抽出開始ボタンが押されました。")
        # --- 4.2. 入力値の取得 ---
        # price_min_str = self.price_min_entry.get()
        # price_max_str = self.price_max_entry.get()
        # count_option = self.count_option_var.get()
        #
        # print(f"最小価格: {price_min_str}")
        # print(f"最大価格: {price_max_str}")
        #
        # if count_option == 1:
        #     count_str = self.count_specific_entry.get()
        #     print(f"抽出オプション: 指定個数, {count_str}個")
        # else:
        #     print("抽出オプション: 全て抽出する")
        
        # --- 4.3. 入力値の検証 ---
        # try:
        #     price_min = int(price_min_str) if price_min_str else 0
        #     price_max = int(price_max_str) if price_max_str else float('inf')
        #     
        #     if price_min > price_max:
        #         messagebox.showerror("入力エラー", "最小価格は最大価格以下である必要があります。")
        #         return
        #
        #     #... ここに実際の抽出処理を記述...
        #
        # except ValueError:
        #     messagebox.showerror("入力エラー", "価格と個数には数値を入力してください。")

if __name__ == "__main__":
    root = tk.Tk()
    app = ExtractionApp(root)
    root.mainloop()