# gui_app.py の中身

import tkinter as tk
from tkinter import messagebox
from func_tle import tle_2_MRAM  # ← ここで本物の処理を呼び出す

def execute_generation(entry_id, label_status, root):
    norad_id = entry_id.get().strip()
    
    # 入力チェック
    if not norad_id or not norad_id.isdigit() or len(norad_id) != 5:
        messagebox.showwarning("入力エラー", "5桁の数字（NORAD ID）を入力してください。")
        return

    output_json = f"TLE_cmd_{norad_id}.json"
    
    try:
        label_status.config(text="通信中・生成中...", fg="blue")
        root.update()
        
        # ★ ここで func_tle.py の処理を実行！
        tle_2_MRAM(norad_id, output_json)
        
        label_status.config(text="完了！", fg="green")
        messagebox.showinfo("成功", f"JSONスクリプトの生成が完了しました！\n出力先: {output_json}")
        
    except Exception as e:
        label_status.config(text="エラー発生", fg="red")
        messagebox.showerror("エラー", f"処理中にエラーが発生しました:\n{e}")

# ==========================================
# main.py から呼び出される起動関数
# ==========================================
def start_app():
    root = tk.Tk()
    root.title("TLE MRAM Command Generator")
    root.geometry("400x200")
    root.eval('tk::PlaceWindow . center')

    label_inst = tk.Label(root, text="5桁のNORAD IDを入力してください:", font=("Arial", 12))
    label_inst.pack(pady=(20, 5))

    entry_id = tk.Entry(root, font=("Arial", 14), width=10, justify="center")
    entry_id.pack(pady=5)
    entry_id.insert(0, "68798")

    label_status = tk.Label(root, text="", font=("Arial", 10))
    
    # ボタン（押されたら execute_generation に必要な変数を渡して実行）
    btn_execute = tk.Button(
        root, text="JSON生成を実行", font=("Arial", 12), 
        command=lambda: execute_generation(entry_id, label_status, root)
    )
    btn_execute.pack(pady=10)
    label_status.pack(pady=5)

    root.mainloop() # 画面の表示をキープ