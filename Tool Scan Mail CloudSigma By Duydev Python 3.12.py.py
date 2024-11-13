import os
import sys
import time
import concurrent.futures

try:
    from bs4 import BeautifulSoup # type: ignore
    from pystyle import Colors, Colorate # type: ignore
    import requests # type: ignore
    from tabulate import tabulate # type: ignore
except ImportError:
    os.system("pip install bs4 pystyle beautifulsoup4 requests tabulate")
    from pystyle import Colors, Colorate # type: ignore
    from bs4 import BeautifulSoup # type: ignore
    from tabulate import tabulate # type: ignore
    import requests # type: ignore

den='[1;90m'
luc='[1;32m'
trang='[1;37m'
red='[1;31m'
vang='[1;33m'
lamd='[1;34m'
lam='[1;36m'
duydev=""
duydev=trang+'~'+red+'['+vang+'⟨⟩'+red+'] '+trang+'➩ '+lam

banners=f"""
██████╗░██╗░░░██╗██╗░░░██╗██████╗░███████╗██╗░░░██╗
██╔══██╗██║░░░██║╚██╗░██╔╝██╔══██╗██╔════╝██║░░░██║
██║░░██║██║░░░██║░╚████╔╝░██║░░██║█████╗░░╚██╗░██╔╝
██║░░██║██║░░░██║░░╚██╔╝░░██║░░██║██╔══╝░░░╚████╔╝░
██████╔╝╚██████╔╝░░░██║░░░██████╔╝███████╗░░╚██╔╝░░
╚═════╝░░╚═════╝░░░░╚═╝░░░╚═════╝░╚══════╝░░░╚═╝░░░\n"""

def clear():
    if os.name == 'nt':  
        os.system('cls')
    else:  
        os.system('clear')

def banner():
    print('[0m', end='')
    clear()
    a = Colorate.Horizontal(Colors.blue_to_green, banners)
    for i in range(len(a)):
        sys.stdout.write(a[i])
        sys.stdout.flush()
    print()

def get_uptime(domain):
    try:
        response = requests.post(
            'https://emailfake.com/check_adres_validation3.php',
            data={'usr': 'charleswhatmore', 'dmn': domain}
        )
        data = response.json()
        return int(data.get("uptime", "N/A"))
    except Exception as e:
        print(f"{duydev} Đã xảy ra lỗi khi kiểm tra uptime: {e}")
        return None

def scrape_domains():
    domains = set()
    try:
        response = requests.get("https://emailfake.com/")
        soup = BeautifulSoup(response.text, 'html.parser')
        domain_elements = soup.select("div.e7m.tt-suggestion p")
        
        for domain in domain_elements:
            domain_name = domain['id']
            domains.add(domain_name)
    except Exception as e:
        print(f"{duydev} Đã xảy ra lỗi trong quá trình thu thập tên miền: {e}")
    return list(domains)

def process_domain(domain, max_uptime, output_file, saved_domains, result):
    if domain in saved_domains:
        result['duplicate_domains'] += 1
        return

    uptime = get_uptime(domain)
    if uptime is not None and uptime <= max_uptime:
        saved_domains.add(domain)
        with open(output_file, 'a') as f:
            f.write(f"{domain} (uptime: {uptime} days)\n")
        result['saved_domains'] += 1
    else:
        result['skipped_domains'] += 1

def print_stats(num_threads, total_domains, saved_domains, skipped_domains, duplicate_domains, current_domains  ):
    stats = [
        ["Nhập Ctrl + C để dừng!!"],
        ["Số luồng", num_threads],
        ["Tổng tên miền", total_domains],
        ["Tên miền đã lưu", saved_domains],
        ["Tên miền bỏ qua", skipped_domains],
        ["Tên miền trùng", duplicate_domains]
    ]
    print(tabulate(stats, headers=["Thống kê", "Giá trị"], tablefmt="grid"))

if __name__ == "__main__":
    clear()
    banner()
    output_file = input(f"\n{duydev} Nhập tên file .txt để lưu kết quả (ví dụ: mail-reg-clsm.txt): ")
    num_domains = int(input(f"{duydev} Nhập số lượng tên miền cần thu thập và kiểm tra uptime: "))
    max_uptime = int(input(f"{duydev} Nhập số ngày uptime tối đa để lưu: "))
    num_threads = int(input(f"{duydev} Nhập số luồng để chạy: "))
    attempt = 1
    saved_domains = set()
    total_domains = 0
    result = {'saved_domains': 0, 'skipped_domains': 0, 'duplicate_domains': 0}

    clear()
    banner()
    print(f"\n{duydev} Ấn Tổ Hợp Phím Ctrl + C Để Dừng Tool")
    print(f"{duydev} Bạn đang chạy {num_threads} luồng (phân chia giữa thu thập và kiểm tra uptime)...")

    try:
        while True:
            print(f"{duydev} Đang thu thập và kiểm tra tên miền Lần {attempt}...")
            num_scrape_threads = num_threads // 2
            num_check_threads = num_threads - num_scrape_threads

            current_domains = 0
            with concurrent.futures.ThreadPoolExecutor(max_workers=num_scrape_threads) as scrape_executor:
                scrape_futures = [scrape_executor.submit(scrape_domains) for _ in range(num_scrape_threads)]
                all_domains = set()

                for future in concurrent.futures.as_completed(scrape_futures):
                    domains = future.result()
                    all_domains.update(domains)

            total_domains += len(all_domains)
            current_domains = len(all_domains)

            if not all_domains:
                print(f"{duydev} Không thu thập được tên miền nào.")
                break

            with concurrent.futures.ThreadPoolExecutor(max_workers=num_check_threads) as check_executor:
                check_futures = [check_executor.submit(process_domain, domain, max_uptime, output_file, saved_domains, result) for domain in list(all_domains)[:num_domains]]
                
                for future in concurrent.futures.as_completed(check_futures):
                    future.result()
            clear()
            banner()
            print_stats(num_threads, total_domains, result['saved_domains'], result['skipped_domains'], result['duplicate_domains'], current_domains)

            attempt += 1
            print(f"{duydev} Đã hết tên miền thu thập trong vòng này. Tiến hành thu thập tiếp lần {attempt}...")
            time.sleep(2)
    except KeyboardInterrupt:
        print(f"{duydev} Người dùng đã dừng chương trình.")
    except Exception as e:
        print(f"{duydev} Đã xảy ra lỗi không xác định: {e}")
    finally:
        print(f"{duydev} Tạm Biệt!")
