import tkinter as tk
from tkinter import ttk, messagebox

# 既存のTLE自動生成関数と、汎用書き込み関数をインポート
from func_tle import tle_2_MRAM
from function.func_generate_json import generate_mram_json  # ← 修正済みのパス

# ==========================================
# タブ1: 既存の TLE -> MRAM 生成処理 (省略せずに記載)
# ==========================================
def execute_tle_generation(entry_id, label_status, root):
    norad_id = entry_id.get().strip()
    
    if not norad_id or not norad_id.isdigit() or len(norad_id) != 5:
        messagebox.showwarning("入力エラー", "5桁の数字（NORAD ID）を入力してください。")
        return

    output_json = f"TLE_cmd_{norad_id}.json"
    
    try:
        label_status.config(text="通信中・生成中...", foreground="blue")
        root.update()
        
        tle_2_MRAM(norad_id, output_json)
        
        label_status.config(text="完了！", foreground="green")
        messagebox.showinfo("成功", f"JSONスクリプトの生成が完了しました！\n出力先: {output_json}")
        
    except Exception as e:
        label_status.config(text="エラー発生", foreground="red")
        messagebox.showerror("エラー", f"処理中にエラーが発生しました:\n{e}")

# ==========================================
# タブ2: 新規の カスタムHex -> MRAM 生成処理
# ==========================================
def execute_custom_generation(text_hex, entry_addr, entry_file, label_status, root):
    hex_data = text_hex.get("1.0", tk.END).strip().replace(" ", "").replace("\n", "")
    addr_str = entry_addr.get().strip()
    filename = entry_file.get().strip()

    if not hex_data:
        messagebox.showwarning("入力エラー", "書き込む16進数データを入力してください。")
        return
    try:
        int(hex_data, 16)
    except ValueError:
        messagebox.showwarning("入力エラー", "データには正しい16進数（0-9, A-F）を入力してください。")
        return

    if not addr_str or not addr_str.isdigit():
        messagebox.showwarning("入力エラー", "ベースアドレスは数字で入力してください。")
        return
    base_address = int(addr_str)

    if not filename:
        filename = "CUSTOM_cmd.json"
    elif not filename.endswith(".json"):
        filename += ".json"

    try:
        label_status.config(text="生成中...", foreground="blue")
        root.update()
        
        generate_mram_json(hex_sequence=hex_data, base_address=base_address, file_out_path=filename)
        
        label_status.config(text="完了！", foreground="green")
        messagebox.showinfo("成功", f"JSONスクリプトの生成が完了しました！\n出力先: {filename}")
        
    except Exception as e:
        label_status.config(text="エラー発生", foreground="red")
        messagebox.showerror("エラー", f"処理中にエラーが発生しました:\n{e}")

# ==========================================
# main.py から呼び出される起動関数
# ==========================================
def start_app():
    root = tk.Tk()
    root.title("MRAM Command Generator")
    root.geometry("500x400")
    root.eval('tk::PlaceWindow . center')

    notebook = ttk.Notebook(root)
    notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    # --- タブ1: TLE自動生成タブ ---
    tab_tle = ttk.Frame(notebook)
    notebook.add(tab_tle, text="TLEから自動生成")

    ttk.Label(tab_tle, text="5桁のNORAD IDを入力してください:", font=("Arial", 12)).pack(pady=(30, 5))
    entry_id = ttk.Entry(tab_tle, font=("Arial", 14), width=10, justify="center")
    entry_id.pack(pady=5)
    entry_id.insert(0, "68798")

    label_status_tle = ttk.Label(tab_tle, text="", font=("Arial", 10))
    btn_execute_tle = ttk.Button(
        tab_tle, text="TLEからJSON生成",
        command=lambda: execute_tle_generation(entry_id, label_status_tle, root)
    )
    btn_execute_tle.pack(pady=20)
    label_status_tle.pack(pady=5)

    # --- タブ2: カスタム入力タブ ---
    tab_custom = ttk.Frame(notebook)
    notebook.add(tab_custom, text="カスタムHex生成")

    frame_file = ttk.Frame(tab_custom)
    frame_file.pack(fill=tk.X, padx=20, pady=(15, 5))
    ttk.Label(frame_file, text="出力ファイル名:").pack(side=tk.LEFT)
    entry_file = ttk.Entry(frame_file, width=30)
    entry_file.pack(side=tk.RIGHT, expand=True, fill=tk.X, padx=(10, 0))
    entry_file.insert(0, "CUSTOM_cmd.json")

    frame_addr = ttk.Frame(tab_custom)
    frame_addr.pack(fill=tk.X, padx=20, pady=5)
    ttk.Label(frame_addr, text="ベースアドレス:").pack(side=tk.LEFT)
    entry_addr = ttk.Entry(frame_addr, width=15)
    entry_addr.pack(side=tk.RIGHT, expand=True, fill=tk.X, padx=(10, 0))
    entry_addr.insert(0, "32768")

    # 【変更点】ラベルにリトルエンディアンであることを明記
    ttk.Label(tab_custom, text="書き込む16進数データ (※リトルエンディアン / スペース・改行無視):", font=("Arial", 9, "bold")).pack(anchor=tk.W, padx=20, pady=(10, 2))
    
    text_hex = tk.Text(tab_custom, height=5, width=40, font=("Consolas", 10))
    text_hex.pack(padx=20, fill=tk.BOTH, expand=True)

    label_status_custom = ttk.Label(tab_custom, text="", font=("Arial", 10))
    btn_execute_custom = ttk.Button(
        tab_custom, text="カスタムJSON生成",
        command=lambda: execute_custom_generation(text_hex, entry_addr, entry_file, label_status_custom, root)
    )
    btn_execute_custom.pack(pady=10)
    label_status_custom.pack(pady=5)

    root.mainloop()

if __name__ == "__main__":
    start_app()