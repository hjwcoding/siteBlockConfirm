import tkinter as tk
from tkinter import ttk, scrolledtext
import threading
import asyncio
import scraper
from scheduler import Scheduler # Import the class
from tuples_list import tuples_list

class PortCheckerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("방화벽 포트 검사기")
        self.root.geometry("1000x700")

        # Instantiate the scheduler, passing the log method as the logger
        self.scheduler = Scheduler(logger=self.log)
        self.is_auto_checking = False

        # Main frame
        main_frame = ttk.Frame(root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # --- 1. Controls Frame ---
        controls_frame = ttk.LabelFrame(main_frame, text="실행 제어", padding="10")
        controls_frame.pack(fill=tk.X, pady=5)

        self.run_single_button = ttk.Button(controls_frame, text="점검 시작", command=self.run_single_check)
        self.run_single_button.pack(side=tk.LEFT, padx=5)

        self.toggle_auto_button = ttk.Button(controls_frame, text="자동 점검 시작", command=self.toggle_auto_check)
        self.toggle_auto_button.pack(side=tk.LEFT, padx=5)

        # --- 2. IP/Port List Frame ---
        list_frame = ttk.LabelFrame(main_frame, text="점검 대상 목록", padding="10")
        list_frame.pack(fill=tk.BOTH, expand=True, pady=5)

        self.tree = ttk.Treeview(list_frame, columns=("Category", "Service", "IP", "Port", "URL"), show="headings")
        self.tree.heading("Category", text="구분")
        self.tree.heading("Service", text="서비스명")
        self.tree.heading("IP", text="IP 주소")
        self.tree.heading("Port", text="포트")
        self.tree.heading("URL", text="URL")

        self.tree.column("Category", width=80)
        self.tree.column("Service", width=150)
        self.tree.column("IP", width=120)
        self.tree.column("Port", width=50)
        self.tree.column("URL", width=200)

        # Scrollbars for the treeview
        vsb = ttk.Scrollbar(list_frame, orient="vertical", command=self.tree.yview)
        hsb = ttk.Scrollbar(list_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        vsb.pack(side=tk.RIGHT, fill=tk.Y)
        hsb.pack(side=tk.BOTTOM, fill=tk.X)
        self.tree.pack(fill=tk.BOTH, expand=True)

        self.load_tuples_list()

        # --- 3. Log Frame ---
        log_frame = ttk.LabelFrame(main_frame, text="실시간 로그", padding="10")
        log_frame.pack(fill=tk.X, pady=5)

        self.log_area = scrolledtext.ScrolledText(log_frame, height=15, wrap=tk.WORD, state='disabled')
        self.log_area.pack(fill=tk.BOTH, expand=True)

        # Ensure scheduler is stopped when the window is closed
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def log(self, message):
        """Inserts a message into the log area. Thread-safe."""
        def _log():
            self.log_area.config(state='normal')
            self.log_area.insert(tk.END, str(message) + "\n")
            self.log_area.see(tk.END)
            self.log_area.config(state='disabled')
        self.root.after(0, _log)

    def load_tuples_list(self):
        """Loads data from tuples_list into the treeview."""
        for item in self.tree.get_children():
            self.tree.delete(item)
        for t in tuples_list:
            self.tree.insert("", tk.END, values=(t[0], t[1], t[4], t[5], t[6]))

    def run_single_check(self):
        """Runs the scraper check once in a separate thread."""
        self.log("단일 점검을 시작합니다...")
        self.run_single_button.config(state='disabled')
        
        check_thread = threading.Thread(target=self._run_async_check)
        check_thread.daemon = True
        check_thread.start()

    def _run_async_check(self):
        """Helper to run the async scraper function and re-enable the button."""
        try:
            # Run the check, passing the GUI's log method as the logger
            asyncio.run(scraper.run_checks(logger=self.log))
            self.log("점검이 완료되었습니다.")
        except Exception as e:
            self.log(f"오류 발생: {e}")
        finally:
            # Re-enable the button on the main thread
            self.root.after(0, lambda: self.run_single_button.config(state='normal'))

    def toggle_auto_check(self):
        """Starts or stops the scheduled checks using the Scheduler class."""
        if self.is_auto_checking:
            self.scheduler.stop()
            self.is_auto_checking = False
            self.toggle_auto_button.config(text="자동 점검 시작")
        else:
            self.scheduler.start()
            self.is_auto_checking = True
            self.toggle_auto_button.config(text="자동 점검 중지")

    def on_closing(self):
        """Handles window closing to ensure background threads are stopped."""
        if self.is_auto_checking:
            self.scheduler.stop()
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = PortCheckerApp(root)
    root.mainloop()
