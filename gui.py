
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import threading
import asyncio
import scraper
from scheduler import Scheduler
from nslookup_ipv4 import nslookup
import json
import os
import sys
import shutil

# --- Helper Functions ---
def get_resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller."""
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# --- Dialog Class ---
class DataEntryDialog(tk.Toplevel):
    def __init__(self, parent, title, data=None):
        super().__init__(parent)
        self.transient(parent)
        self.title(title)
        self.result = None
        self.data = data if data else {'Category': '', 'Service': '', 'IP': '', 'Port': '', 'URL': ''}
        self.entries = {}
        
        form_frame = ttk.Frame(self, padding="10")
        form_frame.pack(fill=tk.BOTH, expand=True)

        fields = ["Category", "Service", "IP", "Port", "URL"]
        for i, field in enumerate(fields):
            ttk.Label(form_frame, text=f"{field}:").grid(row=i, column=0, sticky=tk.W, pady=2)
            entry = ttk.Entry(form_frame, width=40)
            entry.grid(row=i, column=1, sticky=(tk.W, tk.E), pady=2)
            entry.insert(0, self.data.get(field, ''))
            self.entries[field] = entry

        button_frame = ttk.Frame(self, padding="10")
        button_frame.pack(fill=tk.X)
        ttk.Button(button_frame, text="OK", command=self.on_ok).pack(side=tk.RIGHT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=self.on_cancel).pack(side=tk.RIGHT)

        self.grab_set()
        self.protocol("WM_DELETE_WINDOW", self.on_cancel)
        self.wait_window(self)

    def on_ok(self):
        self.result = {field: entry.get() for field, entry in self.entries.items()}
        self.destroy()

    def on_cancel(self):
        self.result = None
        self.destroy()

# --- Main Application Class ---
class PortCheckerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("방화벽 포트 검사기")
        self.root.geometry("1000x800")

        # --- Data Initialization ---
        self.app_data_dir = os.path.join(os.getenv('APPDATA'), 'FirewallChecker')
        os.makedirs(self.app_data_dir, exist_ok=True)
        
        self.tuples_list_path = os.path.join(self.app_data_dir, "tuples_list.json")
        self.domain_list_path = os.path.join(self.app_data_dir, "domain_list.json")

        self.tuples_list = self.initialize_data_file(self.tuples_list_path, "tuples_list.json")
        self.domain_list = self.initialize_data_file(self.domain_list_path, "domain_list.json")

        # --- Scheduler and State ---
        self.scheduler = Scheduler(logger=self.log)
        self.is_auto_checking = False
        self.changes_made = False

        # --- UI Setup ---
        self.setup_ui()
        self.load_all_lists()

    def setup_ui(self):
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        controls_frame = ttk.LabelFrame(main_frame, text="실행 제어", padding="10")
        controls_frame.pack(fill=tk.X, pady=5)
        self.run_full_check_button = ttk.Button(controls_frame, text="전체 점검", command=self.run_full_check)
        self.run_full_check_button.pack(side=tk.LEFT, padx=5)
        self.domain_check_button = ttk.Button(controls_frame, text="도메인 점검", command=self.run_domain_check)
        self.domain_check_button.pack(side=tk.LEFT, padx=5)
        self.auto_check_button = ttk.Button(controls_frame, text="자동 점검 시작", command=self.toggle_auto_check)
        self.auto_check_button.pack(side=tk.LEFT, padx=5)
        self.save_button = ttk.Button(controls_frame, text="변경사항 저장", command=self.save_changes, state='disabled')
        self.save_button.pack(side=tk.RIGHT, padx=5)

        list_frame = ttk.LabelFrame(main_frame, text="점검 대상 목록", padding="10")
        list_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        self.notebook = ttk.Notebook(list_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        full_list_tab = ttk.Frame(self.notebook, padding="5")
        self.notebook.add(full_list_tab, text="전체 목록")
        self.full_list_tree = self.create_treeview(full_list_tab)
        self.add_crud_buttons(full_list_tab, self.add_full_item, self.edit_full_item, self.delete_full_item)

        domain_list_tab = ttk.Frame(self.notebook, padding="5")
        self.notebook.add(domain_list_tab, text="도메인 목록")
        self.domain_list_tree = self.create_treeview(domain_list_tab)
        self.domain_list_tree.tag_configure('failed', background='lightcoral')
        self.add_crud_buttons(domain_list_tab, self.add_domain_item, self.edit_domain_item, self.delete_domain_item)

        log_frame = ttk.LabelFrame(main_frame, text="실시간 로그", padding="10")
        log_frame.pack(fill=tk.X, pady=5, expand=False)
        self.log_area = scrolledtext.ScrolledText(log_frame, height=15, wrap=tk.WORD, state='disabled')
        self.log_area.pack(fill=tk.BOTH, expand=True)

        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def initialize_data_file(self, user_path, default_filename):
        """Loads data from user's AppData, or copies default from bundle if it doesn't exist."""
        if not os.path.exists(user_path):
            self.log(f"{user_path} not found. Copying default data...")
            try:
                default_path = get_resource_path(default_filename)
                shutil.copy2(default_path, user_path)
                self.log(f"Default data copied to {user_path}")
            except Exception as e:
                self.log(f"Error copying default data file: {e}")
                messagebox.showerror("Fatal Error", f"기본 데이터 파일 복사 실패: {e}")
                return []
        
        return self.load_from_json(user_path)

    def load_from_json(self, file_path):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError, FileNotFoundError) as e:
            self.log(f"Error loading {file_path}: {e}")
            messagebox.showerror("Load Error", f"{file_path} 파일을 불러오는 중 오류가 발생했습니다.")
            return []

    def add_crud_buttons(self, parent, add_cmd, edit_cmd, delete_cmd):
        button_frame = ttk.Frame(parent)
        button_frame.pack(fill=tk.X, pady=5)
        ttk.Button(button_frame, text="추가", command=add_cmd).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="수정", command=edit_cmd).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="삭제", command=delete_cmd).pack(side=tk.LEFT, padx=5)

    def create_treeview(self, parent):
        tree_frame = ttk.Frame(parent)
        tree_frame.pack(fill=tk.BOTH, expand=True)
        tree = ttk.Treeview(tree_frame, columns=("Category", "Service", "IP", "Port", "URL"), show="headings")
        tree.heading("Category", text="구분"); tree.heading("Service", text="서비스명"); tree.heading("IP", text="IP 주소"); tree.heading("Port", text="포트"); tree.heading("URL", text="URL")
        tree.column("Category", width=80, anchor=tk.W); tree.column("Service", width=150, anchor=tk.W); tree.column("IP", width=120, anchor=tk.W); tree.column("Port", width=50, anchor=tk.CENTER); tree.column("URL", width=300, anchor=tk.W)
        vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=tree.yview); hsb = ttk.Scrollbar(tree_frame, orient="horizontal", command=tree.xview)
        tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        vsb.pack(side=tk.RIGHT, fill=tk.Y); hsb.pack(side=tk.BOTTOM, fill=tk.X); tree.pack(fill=tk.BOTH, expand=True)
        return tree

    def log(self, message):
        def _log():
            self.log_area.config(state='normal'); self.log_area.insert(tk.END, str(message) + "\n"); self.log_area.see(tk.END); self.log_area.config(state='disabled')
        self.root.after(0, _log)

    def mark_changes(self):
        self.changes_made = True
        self.save_button.config(state='normal')

    def _reload_tree(self, tree, data_list):
        for item in tree.get_children(): tree.delete(item)
        for i, t in enumerate(data_list):
            # Ensure t is a list/tuple with at least 7 elements before accessing index 6
            if len(t) >= 7:
                tree.insert("", tk.END, iid=i, values=(t[0], t[1], t[4], t[5], t[6]))
            else:
                self.log(f"Skipping invalid item in list: {t}")

    def load_all_lists(self):
        self._reload_tree(self.full_list_tree, self.tuples_list)
        self._reload_tree(self.domain_list_tree, self.domain_list)

    def add_item(self, data_list, list_name, reload_func):
        dialog = DataEntryDialog(self.root, f"Add {list_name} Item")
        if dialog.result:
            new_item = [dialog.result['Category'], dialog.result['Service'], '', '', dialog.result['IP'], dialog.result['Port'], dialog.result['URL'], '']
            data_list.append(new_item)
            reload_func()
            self.mark_changes()

    def edit_item(self, tree, data_list, list_name, reload_func):
        selected_iid = tree.focus()
        if not selected_iid: return messagebox.showwarning("No Selection", "수정할 항목을 선택하세요.")
        item_index = int(selected_iid)
        item_data = data_list[item_index]
        dialog_data = {'Category': item_data[0], 'Service': item_data[1], 'IP': item_data[4], 'Port': item_data[5], 'URL': item_data[6]}
        dialog = DataEntryDialog(self.root, f"Edit {list_name} Item", dialog_data)
        if dialog.result:
            data_list[item_index] = [dialog.result['Category'], dialog.result['Service'], item_data[2], item_data[3], dialog.result['IP'], dialog.result['Port'], dialog.result['URL'], item_data[7]]
            reload_func()
            self.mark_changes()

    def delete_item(self, tree, data_list, reload_func):
        selected_iids = tree.selection()
        if not selected_iids: return messagebox.showwarning("No Selection", "삭제할 항목을 선택하세요.")
        indices_to_delete = sorted([int(iid) for iid in selected_iids], reverse=True)
        for index in indices_to_delete: del data_list[index]
        reload_func()
        self.mark_changes()

    def add_full_item(self): self.add_item(self.tuples_list, "Full List", self.load_all_lists)
    def edit_full_item(self): self.edit_item(self.full_list_tree, self.tuples_list, "Full List", self.load_all_lists)
    def delete_full_item(self): self.delete_item(self.full_list_tree, self.tuples_list, self.load_all_lists)

    def add_domain_item(self): self.add_item(self.domain_list, "Domain List", self.load_all_lists)
    def edit_domain_item(self): self.edit_item(self.domain_list_tree, self.domain_list, "Domain List", self.load_all_lists)
    def delete_domain_item(self): self.delete_item(self.domain_list_tree, self.domain_list, self.load_all_lists)

    def run_full_check(self):
        self.log("전체 목록 점검을 시작합니다...")
        self.run_full_check_button.config(state='disabled'); self.domain_check_button.config(state='disabled')
        check_thread = threading.Thread(target=self._run_async_scraper_check, args=(self.tuples_list,))
        check_thread.daemon = True; check_thread.start()

    def _run_async_scraper_check(self, target_list):
        try:
            asyncio.run(scraper.run_checks(target_list, logger=self.log))
            self.log("점검이 완료되었습니다.")
        except Exception as e:
            self.log(f"오류 발생: {e}")
        finally:
            self.root.after(0, lambda: [self.run_full_check_button.config(state='normal'), self.domain_check_button.config(state='normal')])

    def run_domain_check(self):
        # Clear previous highlights
        for item_id in self.domain_list_tree.get_children():
            self.domain_list_tree.item(item_id, tags=())
            
        self.log("도메인 점검 (NSLOOKUP)을 시작합니다...")
        self.run_full_check_button.config(state='disabled'); self.domain_check_button.config(state='disabled')
        domain_thread = threading.Thread(target=self._run_nslookup_check)
        domain_thread.daemon = True; domain_thread.start()

    def _run_nslookup_check(self):
        failed_item_iids = []
        try:
            for i, t in enumerate(self.domain_list):
                domain = t[6]
                if domain:
                    if nslookup(domain, logger=self.log) is None:
                        failed_item_iids.append(str(i))
            self.log("도메인 점검이 완료되었습니다.")
        except Exception as e:
            self.log(f"오류 발생: {e}")
        finally:
            self.root.after(0, self.update_ui_after_domain_check, failed_item_iids)

    def update_ui_after_domain_check(self, failed_item_iids):
        self.run_full_check_button.config(state='normal')
        self.domain_check_button.config(state='normal')
        if failed_item_iids:
            self.log(f"실패한 도메인 {len(failed_item_iids)}개에 음영을 적용합니다.")
            for item_id in failed_item_iids:
                if self.domain_list_tree.exists(item_id):
                    self.domain_list_tree.item(item_id, tags=('failed',))

    def save_changes(self):
        self.log("변경사항을 JSON 파일에 저장합니다...")
        try:
            with open(self.tuples_list_path, "w", encoding="utf-8") as f:
                json.dump(self.tuples_list, f, ensure_ascii=False, indent=4)
            with open(self.domain_list_path, "w", encoding="utf-8") as f:
                json.dump(self.domain_list, f, ensure_ascii=False, indent=4)
            self.log("저장 완료.")
            self.changes_made = False
            self.save_button.config(state='disabled')
        except Exception as e:
            messagebox.showerror("Save Error", f"파일 저장 중 오류가 발생했습니다: {e}")
            self.log(f"파일 저장 오류: {e}")

    def toggle_auto_check(self):
        if self.is_auto_checking:
            self.scheduler.stop(); self.is_auto_checking = False; self.auto_check_button.config(text="자동 점검 시작")
        else:
            self.scheduler.start(); self.is_auto_checking = True; self.auto_check_button.config(text="자동 점검 중지")

    def on_closing(self):
        if self.changes_made:
            if not messagebox.askyesno("Unsaved Changes", "저장하지 않은 변경사항이 있습니다. 정말로 종료하시겠습니까?"):
                return # Do not close
        
        if self.is_auto_checking: self.scheduler.stop()
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = PortCheckerApp(root)
    root.mainloop()
