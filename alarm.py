import smtplib
from email.mime.text import MIMEText

def send_alert(ip, port, result):
    sender = "scraping1@kwic.co.kr"   # 다우오피스 메일 주소
    password = "kwic5539!"       # 다우오피스 계정 비번
    receiver = "scraping1@kwic.co.kr"  # 받는 사람 메일

    msg = MIMEText(f"🚨 {ip}:{port} 상태가 {result} 입니다.")
    msg["Subject"] = "포트 점검 알림"
    msg["From"] = sender
    msg["To"] = receiver

    try:
        # 465 SSL 연결
        with smtplib.SMTP_SSL("smtp.daouoffice.com", 587) as server:
            server.ehlo()
            server.starttls()
            server.login(sender, password)
            server.send_message(msg)
        print(f"✅ 알림 발송 성공: {ip}:{port} → {result}")

    except Exception as e:
        print(f"❌ 메일 발송 실패: {e}")
if __name__ == "__main__":
    send_alert('203.243.39.11','80','open')