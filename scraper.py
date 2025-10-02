import asyncio
import alarm
from playwright.async_api import async_playwright
from datetime import datetime

from tuples_list import tuples_list

async def check_port(ip: str, port: str) -> str:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=False)  # headless=False면 실제 창 보임
            # browser = await p.chromium.launch(headless=False, slow_mo=500) # slow_mo: 동작 속도 조절(0.5초)

            page = await browser.new_page()
            await page.goto("https://ko.rakko.tools/tools/15/")  # 포트 검사기 메인

            html = await page.content()
            if "Begin" in html:
                print("과부하로 인한 캡차 발생...")
                while True:
                    print("10초 대기 후 재시도...")
                    await page.wait_for_timeout(10000)
                    html = await page.goto("https://ko.rakko.tools/tools/15/")  # 포트 검사기 메인
                    html = await page.content()
                    if "검사" in html:
                        break

            # 입력창 찾기 (보통 첫 번째 input이 IP, 두 번째 input이 포트)
            # IP/Host 입력
            await page.fill("#textHostOrIp", ip)   # 원하는 IP 또는 호스트

            # 포트 입력
            await page.fill("#portNumbers", port)     # 원하는 포트들 (쉼표로 구분 가능)

            # "검사" 버튼 클릭
            try:
                await page.click("#jsCheckPort")
                print("버튼 클릭 성공")
            except:
                await page.locator('button:has-text("검사")').click()
                print("버튼 클릭 실패")


            # 결과 span(#ps_res_1)이 표시될 때까지 대기
            await page.wait_for_selector("#ps_res_1", timeout=20000)

            # span의 텍스트 추출
            result_text = await page.locator("#ps_res_1").inner_text()
            print("검사 결과:", result_text)   # open / closed 등 출력됨

            await browser.close()
            return result_text

async def run_checks():
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    for t in tuples_list:
        result = await check_port(t[4], t[5])
        if result.lower() != "open":
            # send_alert(ip, port, result)  # 알림 함수 호출
            print(f"{t[4]}:{t[5]} 🚨 {result}")
            # 현재 시간으로 파일명 생성
            txt_filename = f"결과_{timestamp}.txt"
            with open(txt_filename, 'a', encoding='utf-8') as f:
                f.write("=" * 80 + "\n")
                f.write("검증 결과 리포트\n")
                f.write("=" * 80 + "\n\n")
                f.write(f"{t[0]} - {t[1]}\n")
                f.write(f"    업무명: {t[2]}\n")
                f.write(f"    IP: {t[4]}:{t[5]}\n")
                f.write(f"    PORT: {t[5]}\n")
                f.write(f"    URL: {t[6]}\n")
                f.write("-" * 80 + "\n")

                # f.write(f"\n총 {len(result_list)}개 항목 검증 완료\n")

            print(f"✅ 텍스트 파일 저장 완료: {txt_filename}")
        else:
            print(f"{t[4]}:{t[5]} ✅ open")
    else:
        print("검증이 완료 되었습니다")

if __name__ == "__main__":
    asyncio.run(run_checks())
