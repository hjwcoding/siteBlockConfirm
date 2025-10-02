import asyncio
import alarm
from playwright.async_api import async_playwright

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
    for t in tuples_list:
        result = await check_port(t[4], t[5])
        if result.lower() != "open":
            # send_alert(ip, port, result)  # 알림 함수 호출
            print(f"{t[4]}:{t[5]} 🚨 {result}")
        else:
            print(f"{t[4]}:{t[5]} ✅ open")

if __name__ == "__main__":
    asyncio.run(run_checks())
