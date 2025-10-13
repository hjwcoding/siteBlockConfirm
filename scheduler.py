import schedule
import asyncio
import scraper
import time
import threading

class Scheduler:
    def __init__(self, logger=print):
        self.logger = logger
        self._is_running = False
        self.thread = None
        self.job_func = lambda: asyncio.run(scraper.run_checks(logger=self.logger))

        # Clear any previous schedules and set up the new job
        schedule.clear()
        schedule.every(5).seconds.do(self.job_func)

    def _run_continuously(self):
        self.logger("포트 점검 스케줄러 시작됨.")
        while self._is_running:
            schedule.run_pending()
            time.sleep(1)
        self.logger("포트 점검 스케줄러 중지됨.")

    def start(self):
        if self._is_running:
            self.logger("스케줄러가 이미 실행 중입니다.")
            return

        self._is_running = True
        self.thread = threading.Thread(target=self._run_continuously)
        self.thread.daemon = True
        self.thread.start()

    def stop(self):
        if not self._is_running:
            self.logger("스케줄러가 실행 중이 아닙니다.")
            return
        
        self._is_running = False
        # The thread will exit the loop on its own.
        # If you need to wait for it to finish:
        # self.thread.join()

# --- Original script functionality for standalone execution ---
if __name__ == "__main__":
    print("스케줄러를 독립적으로 실행합니다. 중지하려면 Ctrl+C를 누르세요.")
    
    # In standalone mode, we just use the default print logger.
    main_scheduler = Scheduler()
    main_scheduler.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n스케줄러를 중지합니다...")
        main_scheduler.stop()
        print("스케줄러가 중지되었습니다.")