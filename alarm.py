import smtplib
from email.mime.text import MIMEText

def send_alert(ip, port, result):
    msg = MIMEText(f"🚨 {ip}:{port} 상태가 {result} 입니다.")
    msg["Subject"] = "포트 점검 알림"
    msg["From"] = "alert@example.com"
    msg["To"] = "you@example.com"

    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls()
        server.login("your_gmail@gmail.com", "앱비밀번호")
        server.send_message(msg)

    print(f"알림 발송: {ip}:{port} → {result}")
