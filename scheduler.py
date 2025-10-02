import schedule
import asyncio
import scraper
import time

def job():
    print("Running scheduled job...")
    asyncio.run(scraper.run_checks())

# 1분마다 실행
# schedule.every(1).minutes.do(job)
schedule.every(5).seconds.do(job)

print("포트 점검 스케줄러 실행 중...")
while True:
    schedule.run_pending()
    time.sleep(1)