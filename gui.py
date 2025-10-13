import tkinter as tk
from tkinter import ttk, scrolledtext
import threading
import asyncio
import scraper
from scheduler import Scheduler
from tuples_list import tuples_list
from domain_list import domain_list
from nslookup_ipv4 import nslookup

class PortCheckerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("방화벽 포트 검사기")
        self.root.geometry("1000x700")

        self.scheduler = Scheduler(logger=self.log)
        self.is_auto_checking = False

        main_frame = ttk.Frame(root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # --- 1. Controls Frame ---
        controls_frame = ttk.LabelFrame(main_frame, text="실행 제어", padding="10")
        controls_frame.pack(fill=tk.X, pady=5)

        self.run_single_button = ttk.Button(controls_frame, text="전체 점검", command=self.run_full_check)
        self.run_single_button.pack(side=tk.LEFT, padx=5)

        self.domain_check_button = ttk.Button(controls_frame, text="도메인 점검", command=self.run_domain_check)
        self.domain_check_button.pack(side=tk.LEFT, padx=5)

        self.auto_check_button = ttk.Button(controls_frame, text="자동 점검 시작", command=self.toggle_auto_check)
        self.auto_check_button.pack(side=tk.LEFT, padx=5)

        # --- 2. IP/Port List Frame with Tabs ---
        list_frame = ttk.LabelFrame(main_frame, text="점검 대상 목록", padding="10")
        list_frame.pack(fill=tk.BOTH, expand=True, pady=5)

        self.notebook = ttk.Notebook(list_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        # Tab 1: Full List
        full_list_tab = ttk.Frame(self.notebook)
        self.notebook.add(full_list_tab, text="전체 목록")
        self.full_list_tree = self.create_treeview(full_list_tab)
        self.load_tuples_list()

        # Tab 2: Domain List
        domain_list_tab = ttk.Frame(self.notebook)
        self.notebook.add(domain_list_tab, text="도메인 목록 (중복제거)")
        self.domain_list_tree = self.create_treeview(domain_list_tab)
        self.load_domain_list()

        # --- 3. Log Frame ---
        log_frame = ttk.LabelFrame(main_frame, text="실시간 로그", padding="10")
        log_frame.pack(fill=tk.X, pady=5, expand=False)

        self.log_area = scrolledtext.ScrolledText(log_frame, height=15, wrap=tk.WORD, state='disabled')
        self.log_area.pack(fill=tk.BOTH, expand=True)

        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def create_treeview(self, parent):
        """Helper function to create a configured Treeview."""
        tree = ttk.Treeview(parent, columns=("Category", "Service", "IP", "Port", "URL"), show="headings")
        tree.heading("Category", text="구분")
        tree.heading("Service", text="서비스명")
        tree.heading("IP", text="IP 주소")
        tree.heading("Port", text="포트")
        tree.heading("URL", text="URL")

        tree.column("Category", width=80, anchor=tk.W)
        tree.column("Service", width=150, anchor=tk.W)
        tree.column("IP", width=120, anchor=tk.W)
        tree.column("Port", width=50, anchor=tk.CENTER)
        tree.column("URL", width=300, anchor=tk.W)

        vsb = ttk.Scrollbar(parent, orient="vertical", command=tree.yview)
        hsb = ttk.Scrollbar(parent, orient="horizontal", command=tree.xview)
        tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        vsb.pack(side=tk.RIGHT, fill=tk.Y)
        hsb.pack(side=tk.BOTTOM, fill=tk.X)
        tree.pack(fill=tk.BOTH, expand=True)
        return tree

    def log(self, message):
        """Inserts a message into the log area. Thread-safe."""
        def _log():
            self.log_area.config(state='normal')
            self.log_area.insert(tk.END, str(message) + "\n")
            self.log_area.see(tk.END)
            self.log_area.config(state='disabled')
        self.root.after(0, _log)

    def load_tuples_list(self):
        """Loads data from tuples_list into the full list treeview."""
        for item in self.full_list_tree.get_children():
            self.full_list_tree.delete(item)
        for t in tuples_list:
            self.full_list_tree.insert("", tk.END, values=(t[0], t[1], t[4], t[5], t[6]))

    def load_domain_list(self):
        """Loads data from domain_list into the domain list treeview."""
        for item in self.domain_list_tree.get_children():
            self.domain_list_tree.delete(item)
        for t in domain_list:
            self.domain_list_tree.insert("", tk.END, values=(t[0], t[1], t[4], t[5], t[6]))

    def run_full_check(self):
        """Runs the scraper check on the full list in a separate thread."""
        self.log("전체 목록 점검을 시작합니다...")
        self.run_single_button.config(state='disabled')
        self.domain_check_button.config(state='disabled')

        check_thread = threading.Thread(target=self._run_async_scraper_check, args=(tuples_list,))
        check_thread.daemon = True
        check_thread.start()

    def _run_async_scraper_check(self, target_list):
        """Helper to run the async scraper function."""
        try:
            asyncio.run(scraper.run_checks(target_list, logger=self.log))
            self.log("점검이 완료되었습니다.")
        except Exception as e:
            self.log(f"오류 발생: {e}")
        finally:
            self.root.after(0, lambda: self.run_single_button.config(state='normal'))
            self.root.after(0, lambda: self.domain_check_button.config(state='normal'))

    def run_domain_check(self):
        """Runs the nslookup check on the unique domain list."""
        self.log("도메인 점검 (NSLOOKUP)을 시작합니다...")
        self.run_single_button.config(state='disabled')
        self.domain_check_button.config(state='disabled')

        domain_thread = threading.Thread(target=self._run_nslookup_check)
        domain_thread.daemon = True
        domain_thread.start()

    def _run_nslookup_check(self):
        try:
            for t in domain_list:
                domain = t[6]
                if domain:
                    nslookup(domain, logger=self.log)
            self.log("도메인 점검이 완료되었습니다.")
        except Exception as e:
            self.log(f"오류 발생: {e}")
        finally:
            self.root.after(0, lambda: self.run_single_button.config(state='normal'))
            self.root.after(0, lambda: self.domain_check_button.config(state='normal'))

    def toggle_auto_check(self):
        """Starts or stops the scheduled checks."""
        if self.is_auto_checking:
            self.scheduler.stop()
            self.is_auto_checking = False
            self.auto_check_button.config(text="자동 점검 시작")
        else:
            self.scheduler.start()
            self.is_auto_checking = True
            self.auto_check_button.config(text="자동 점검 중지")

    def on_closing(self):
        """Handles window closing to ensure background threads are stopped."""
        if self.is_auto_checking:
            self.scheduler.stop()
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = PortCheckerApp(root)
    root.mainloop()