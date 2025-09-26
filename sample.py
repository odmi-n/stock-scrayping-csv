import tkinter as tk
from tkinter import ttk
import threading
import queue
import time

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Safe Tk Template")
        self.geometry("360x160")

        # ---- UI ----
        self.label = ttk.Label(self, text="Ready")
        self.label.pack(pady=10)

        self.start_btn = ttk.Button(self, text="Start long task", command=self.start_task)
        self.start_btn.pack()

        self.progress = ttk.Progressbar(self, mode="indeterminate")
        self.progress.pack(fill="x", padx=12, pady=8)

        # 画像を使うなら self.photo = tk.PhotoImage(file="...") のように「selfで保持」
        # self.iconphoto(False, self.photo)

        # ---- 通信路（スレッド→UI）----
        self.q = queue.Queue()
        self.after(100, self._poll_queue)  # afterでイベントループを塞がない

    def start_task(self):
        self.start_btn.config(state="disabled")
        self.progress.start(10)
        t = threading.Thread(target=self._worker, daemon=True)
        t.start()

    def _worker(self):
        # 長時間処理はバックグラウンドで。UIは触らない！
        for i in range(5):
            time.sleep(0.8)
            self.q.put(("progress", f"Step {i+1}/5"))
        self.q.put(("done", "All done"))

    def _poll_queue(self):
        try:
            while True:
                kind, msg = self.q.get_nowait()
                if kind == "progress":
                    self.label.config(text=msg)  # UI更新はメインスレッド
                elif kind == "done":
                    self.progress.stop()
                    self.start_btn.config(state="normal")
                    self.label.config(text=msg)
        except queue.Empty:
            pass
        finally:
            self.after(100, self._poll_queue)

if __name__ == "__main__":
    app = App()
    app.mainloop()
