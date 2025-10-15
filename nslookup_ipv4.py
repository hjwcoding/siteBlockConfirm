import socket

def nslookup(domain, logger=print):
    """
    도메인의 IPv4 주소만 간단히 조회합니다.
    """
    try:
        # 도메인에서 불필요한 문자(예: 콤마) 제거
        # https:// 제거해야함
        cleaned_domain = domain.strip().replace(',', '').replace('https://', '').split('/')[0]
        if not cleaned_domain:
            return "빈 도메인입니다. domain_list.py 파일을 확인하세요."
        ip_address = socket.gethostbyname(cleaned_domain)
        logger(f"IP 확인 성공! :: {cleaned_domain} -> {ip_address}")
        return ip_address
    except socket.gaierror:
        logger(f"오류: '{domain}'을(를) 찾을 수 없습니다.")
        return None

# if __name__ == "__main__":
# # 테스트할 도메인들
#     domains = ["google.com", "naver.com", "github.com"]

#     for domain in domains:
#         nslookup(domain)
#         print("-" * 40)