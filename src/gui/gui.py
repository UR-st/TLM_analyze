import tkinter as tk
import sys
from tkinter import ttk, messagebox

# 既存のTLE自動生成関数と、汎用書き込み関数をインポート
from function.func_tle import tle_2_MRAM
from function.func_generate_json import generate_mram_json  # ← 修正済みのパス

MODE_TLE = "tle"
MODE_CUSTOM = "custom"


def center_window(window):
    window.update_idletasks()
    width = window.winfo_width()
    height = window.winfo_height()
    x = (window.winfo_screenwidth() - width) // 2
    y = (window.winfo_screenheight() - height) // 2
    window.geometry(f"+{x}+{y}")


# ==========================================
# タブ1: 既存の TLE -> MRAM 生成処理 (省略せずに記載)
# ==========================================
def execute_tle_generation(entry_id, entry_app_id, label_status, root):
    norad_id = entry_id.get().strip()
    
    if not norad_id or not norad_id.isdigit() or len(norad_id) != 5:
        messagebox.showwarning("入力エラー", "5桁の数字（NORAD ID）を入力してください。")
        return

    app_id_str = entry_app_id.get().strip()
    if not app_id_str or not app_id_str.isdigit():
        messagebox.showwarning("入力エラー", "AM_INITIALIZE_APP app_id は数値で入力してください。")
        return
    app_id = int(app_id_str)

    output_json = f"TLE_cmd_{norad_id}.json"
    
    try:
        label_status.config(text="通信中・生成中...", foreground="blue")
        root.update()
        
        tle_2_MRAM(norad_id, output_json, app_id=app_id)
        
        label_status.config(text="完了！", foreground="green")
        messagebox.showinfo("成功", f"JSONスクリプトの生成が完了しました！\n出力先: {output_json}")
        
    except Exception as e:
        label_status.config(text="エラー発生", foreground="red")
        messagebox.showerror("エラー", f"処理中にエラーが発生しました:\n{e}")

# ==========================================
# タブ2: 新規の カスタムHex -> MRAM 生成処理
# ==========================================
def execute_custom_generation(text_hex, entry_addr, entry_file, entry_app_id, label_status, root):
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

    app_id_str = entry_app_id.get().strip()
    if not app_id_str or not app_id_str.isdigit():
        messagebox.showwarning("入力エラー", "AM_INITIALIZE_APP app_id は数値で入力してください。")
        return
    app_id = int(app_id_str)

    if not filename:
        filename = "CUSTOM_cmd.json"
    elif not filename.endswith(".json"):
        filename += ".json"

    try:
        label_status.config(text="生成中...", foreground="blue")
        root.update()
        
        generate_mram_json(hex_sequence=hex_data, base_address=base_address, file_out_path=filename, app_id=app_id)
        
        label_status.config(text="完了！", foreground="green")
        messagebox.showinfo("成功", f"JSONスクリプトの生成が完了しました！\n出力先: {filename}")
        
    except Exception as e:
        label_status.config(text="エラー発生", foreground="red")
        messagebox.showerror("エラー", f"処理中にエラーが発生しました:\n{e}")

# ==========================================
# main.py から呼び出される起動関数
# ==========================================
def select_startup_mode():
    selector = tk.Tk()
    selector.title("起動モード選択")
    selector.geometry("360x190")
    selector.resizable(False, False)
    center_window(selector)

    open_windows = {}
    tle_var = tk.BooleanVar(value=False)
    custom_var = tk.BooleanVar(value=False)

    frame = ttk.Frame(selector, padding=20)
    frame.pack(fill=tk.BOTH, expand=True)

    ttk.Label(frame, text="表示するウィンドウを選択してください。", font=("Arial", 11)).pack(anchor=tk.W, pady=(0, 12))

    def close_generator_window(mode):
        existing_window = open_windows.pop(mode, None)
        if existing_window is not None and existing_window.winfo_exists():
            existing_window.destroy()

    def show_generator_window(mode):
        existing_window = open_windows.get(mode)
        if existing_window is not None and existing_window.winfo_exists():
            existing_window.lift()
            existing_window.focus_force()
            return

        open_windows[mode] = open_generator_window(selector, mode, open_windows, on_generator_window_closed)

    def on_generator_window_closed(mode):
        open_windows.pop(mode, None)
        if mode == MODE_TLE:
            tle_var.set(False)
        elif mode == MODE_CUSTOM:
            custom_var.set(False)

    def on_tle_checked():
        if tle_var.get():
            custom_var.set(False)
            close_generator_window(MODE_CUSTOM)
            show_generator_window(MODE_TLE)
        else:
            close_generator_window(MODE_TLE)

    def on_custom_checked():
        if custom_var.get():
            tle_var.set(False)
            close_generator_window(MODE_TLE)
            show_generator_window(MODE_CUSTOM)
        else:
            close_generator_window(MODE_CUSTOM)

    ttk.Checkbutton(
        frame,
        text="NoradIDからMRAM変更コマンド生成",
        variable=tle_var,
        command=on_tle_checked,
    ).pack(anchor=tk.W, pady=4)
    ttk.Checkbutton(
        frame,
        text="一般的なMRAM変更コマンド生成",
        variable=custom_var,
        command=on_custom_checked,
    ).pack(anchor=tk.W, pady=4)

    def on_closing():
        selector.destroy()
        sys.exit()

    selector.protocol("WM_DELETE_WINDOW", on_closing)
    selector.mainloop()


def build_tle_window(parent, root):
    ttk.Label(parent, text="5桁のNORAD IDを入力してください:", font=("Arial", 12)).pack(pady=(30, 5))
    entry_id = ttk.Entry(parent, font=("Arial", 14), width=10, justify="center")
    entry_id.pack(pady=5)
    entry_id.insert(0, "68798")

    frame_tle_app = ttk.Frame(parent)
    frame_tle_app.pack(fill=tk.X, padx=120, pady=(10, 5))
    ttk.Label(frame_tle_app, text="AM_INITIALIZE_APP app_id:").pack(side=tk.LEFT)
    entry_tle_app_id = ttk.Entry(frame_tle_app, width=8, justify="center")
    entry_tle_app_id.pack(side=tk.RIGHT)
    entry_tle_app_id.insert(0, "188")

    label_status_tle = ttk.Label(parent, text="", font=("Arial", 10))
    btn_execute_tle = ttk.Button(
        parent, text="TLEからJSON生成",
        command=lambda: execute_tle_generation(entry_id, entry_tle_app_id, label_status_tle, root)
    )
    btn_execute_tle.pack(pady=20)
    label_status_tle.pack(pady=5)


def build_custom_window(parent, root):
    frame_file = ttk.Frame(parent)
    frame_file.pack(fill=tk.X, padx=20, pady=(15, 5))
    ttk.Label(frame_file, text="出力ファイル名:").pack(side=tk.LEFT)
    entry_file = ttk.Entry(frame_file, width=30)
    entry_file.pack(side=tk.RIGHT, expand=True, fill=tk.X, padx=(10, 0))
    entry_file.insert(0, "CUSTOM_cmd.json")

    frame_addr = ttk.Frame(parent)
    frame_addr.pack(fill=tk.X, padx=20, pady=5)
    ttk.Label(frame_addr, text="開始アドレス:").pack(side=tk.LEFT)
    entry_addr = ttk.Entry(frame_addr, width=15)
    entry_addr.pack(side=tk.RIGHT, expand=True, fill=tk.X, padx=(10, 0))
    entry_addr.insert(0, "32768")

    frame_custom_app = ttk.Frame(parent)
    frame_custom_app.pack(fill=tk.X, padx=20, pady=5)
    ttk.Label(frame_custom_app, text="AM_INITIALIZE_APP app_id:").pack(side=tk.LEFT)
    entry_custom_app_id = ttk.Entry(frame_custom_app, width=15)
    entry_custom_app_id.pack(side=tk.RIGHT, expand=True, fill=tk.X, padx=(10, 0))
    entry_custom_app_id.insert(0, "188")

    # 【変更点】ラベルにリトルエンディアンであることを明記
    ttk.Label(parent, text="書き込む16進数データ (※リトルエンディアン / スペース・改行無視):", font=("Arial", 9, "bold")).pack(anchor=tk.W, padx=20, pady=(10, 2))
    
    text_hex = tk.Text(parent, height=5, width=40, font=("Consolas", 10))
    text_hex.pack(padx=20, fill=tk.BOTH, expand=True)

    label_status_custom = ttk.Label(parent, text="", font=("Arial", 10))
    btn_execute_custom = ttk.Button(
        parent, text="カスタムJSON生成",
        command=lambda: execute_custom_generation(text_hex, entry_addr, entry_file, entry_custom_app_id, label_status_custom, root)
    )
    btn_execute_custom.pack(pady=10)
    label_status_custom.pack(pady=5)


def open_generator_window(selector, mode, open_windows, on_closed):
    root = tk.Toplevel(selector)
    if mode == MODE_TLE:
        root.title("TLE MRAM Command Generator")
        root.geometry("500x280")
    else:
        root.title("MRAM Command Generator")
        root.geometry("500x450")
    center_window(root)

    def on_closing():
        open_windows.pop(mode, None)
        root.destroy()
        on_closed(mode)

    root.protocol("WM_DELETE_WINDOW", on_closing)

    content = ttk.Frame(root, padding=10)
    content.pack(fill=tk.BOTH, expand=True)
    if mode == MODE_TLE:
        build_tle_window(content, root)
    else:
        build_custom_window(content, root)

    root.lift()
    root.focus_force()
    return root


def start_app():
    select_startup_mode()

if __name__ == "__main__":
    start_app()
