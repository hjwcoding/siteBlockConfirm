import asyncio
import alarm
from playwright.async_api import async_playwright
from datetime import datetime
from tuples_list import tuples_list

# logger 함수를 인자로 받도록 수정
async def check_port(page, ip: str, port: str, logger=print) -> str:
    try:
        await page.goto("https://ko.rakko.tools/tools/15/")  # 포트 검사기 메인
        html = await page.content()
        if "Begin" in html:
            logger("과부하로 인한 캡차 발생... 10초 대기 후 재시도...")
            await asyncio.sleep(10)
            await page.reload()
            # Potentially add a retry limit here if needed

        # IP/Host 입력
        await page.fill("#textHostOrIp", ip)
        # 포트 입력
        await page.fill("#portNumbers", port)
        # "검사" 버튼 클릭
        await page.click("#jsCheckPort")

        # 결과 span(#ps_res_1)이 표시될 때까지 대기
        await page.wait_for_selector("#ps_res_1", timeout=30000)

        # span의 텍스트 추출
        result_text = await page.locator("#ps_res_1").inner_text()
        logger(f"검사 결과: {result_text}")
        return result_text

    except Exception as e:
        logger(f"포트 검사 중 오류 발생: {e}")
        error_element = await page.query_selector("div.error_area p")
        text = ''
        if error_element:
            text = await error_element.inner_text()

        if "데이터 수집에 실패했습니다" in text:
            logger("해당 IP/포트는 존재하지 않는 항목입니다.")
            return "해당 IP/포트는 존재하지 않는 항목입니다."

        return f"오류: {text or '알 수 없는 오류'}"

async def run_checks(target_list, logger=print):
    async with async_playwright() as p:
        # browser = await p.chromium.launch(headless=False, slow_mo=500)  # headless=False면 실제 창 보임
        browser = await p.chromium.launch(headless=True, slow_mo=500) # slow_mo: 동작 속도 조절(0.5초)
        page = await browser.new_page()

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        for t in target_list: # Use the passed-in list
            result = await check_port(page, t[4], t[5], logger=logger)
            logger(f"결과값 :::: 🚨 {result}")
            if result.lower() != "open" :
                # send_alert(ip, port, result)  # 알림 함수 호출
                logger(f"{t[4]}:{t[5]} 🚨 {result}")
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
                    f.write(f"    STATUS: {result}")
                    f.write("-" * 80 + "\n")

                    # f.write(f"\n총 {len(result_list)}개 항목 검증 완료\n")
                logger(f"✅ 텍스트 파일 저장 완료: {txt_filename}")
            else:
                logger(f"{t[4]}:{t[5]} ✅ open")

        logger("검증이 완료 되었습니다")
        await browser.close() # Close the browser when done

if __name__ == "__main__":
    # Pass the global list when running as a standalone script
    asyncio.run(run_checks(tuples_list))
