import requests
import cloudscraper
import cfscrape
import brotli

proxy_list = [
    "45.127.248.127:5128:oahhklfb:htkcan1qkkqa",
    # "64.64.118.149:6732:oahhklfb:htkcan1qkkqa",
    # "157.52.253.244:6204:oahhklfb:htkcan1qkkqa",
    # "167.160.180.203:6754:oahhklfb:htkcan1qkkqa",
    # "166.88.58.10:5735:oahhklfb:htkcan1qkkqa",
    # "173.0.9.70:5653:oahhklfb:htkcan1qkkqa",
    # "45.151.162.198:6600:oahhklfb:htkcan1qkkqa",
    # "204.44.69.89:6342:oahhklfb:htkcan1qkkqa",
    # "173.0.9.209:5792:oahhklfb:htkcan1qkkqa",
    # "206.41.172.74:6634:oahhklfb:htkcan1qkkqa"
]

def format_proxy_url(proxy):
    host, port, username, password = proxy.split(':')
    return f"http://{username}:{password}@{host}:{port}"

test_url = "https://cyberbackgroundchecks.com"
headers = {
    # "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "accept-encoding": "br",
    # "accept-encoding": "gzip, deflate, br, zstd",
    # "accept-language": "en-US,en;q=0.9",
    # "cache-control": "max-age=0",
    # "cookie": f"__qca={session.cookies.get('__qca')}; __qca={session.cookies.get('__qca')}; _gcl_au={session.cookies.get('_gcl_au')}; _lr_env_src_ats={session.cookies.get('_lr_env_src_ats')}; __qca={session.cookies.get('__qca')}; _gid={session.cookies.get('_gid')}; gcid_first={session.cookies.get('gcid_first')}; __cf_bm={session.cookies.get('__cf_bm')}; _lr_retry_request={session.cookies.get('_lr_retry_request')}; cf_clearance={session.cookies.get('cf_clearance')}; cto_bundle=m86w119pN2hYTXRpNFA1bDMxNkpHODVsUWc3UFM4bFU1QnFvOVZ4OUVrZnVMV3dHblRyT1FTczRPODNhclMwdXNOc2NxS21qMHF6Mm9OM3FSN0hiS1JWa0Z5ZmFTVnBmbTRkTno3Y0Zqd1FkRmFMQkxMNFpEWVNHYUx2S1JUR0d4TVBmNkxNc0E1TGlWY1ZVNTA5TzNrJTJGeFRTRm5FJTJGTFRqVGd2WHRHclBmYTVHSk1jJTNE; .AspNetCore.Antiforgery.tWHp3xc7ZGI={session.cookies.get('.AspNetCore.Antiforgery.tWHp3xc7ZGI')}; _ga_ETWB2J0GG5={session.cookies.get('_ga_ETWB2J0GG5')}; _ga={session.cookies.get('_ga')}; _dc_gtm_UA-133553439-1={session.cookies.get('_dc_gtm_UA-133553439-1')}; FCNEC={session.cookies.get('FCNEC')}; _gat_UA-133553439-1={session.cookies.get('_gat_UA-133553439-1')}; __gads={session.cookies.get('__gads')}; __gpi={session.cookies.get('__gpi')}; __eoi={session.cookies.get('__eoi')}",
    # "priority": "u=0, i",
    # "sec-ch-ua": '"Not)A;Brand";v="99", "Google Chrome";v="127", "Chromium";v="127"',
    # "sec-ch-ua-mobile": "?0",
    # "sec-ch-ua-platform": '"Windows"',
    # "sec-fetch-dest": "document",
    # "sec-fetch-mode": "navigate",
    # "sec-fetch-site": "same-origin",
    # "sec-fetch-user": "?1",
    # "upgrade-insecure-requests": "1",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36",
    }

for proxy in proxy_list:
    proxy_url = format_proxy_url(proxy)
    proxies = {
        "http": proxy_url,
        "https": proxy_url,
    }
    
    try:
        scraper = cloudscraper.create_scraper()
        scraper.headers.update(headers)
        res = scraper.get(test_url, proxies=proxies)

        if res.headers.get('Content-Encoding') == 'br':
            decompressed_data = brotli.decompress(res.content)
            content = decompressed_data.decode('utf-8')
        else:
            content = res.text

        if 'you have been blocked' not in res.text.lower():
            print(f"Proxy {proxy} did not block access.")

            with open('cloudscraper.html', 'w') as f:
                f.write(content)

        
    except Exception as e:
        print(f"Error with proxy {proxy}: {e}")

    try:
        res1 = requests.get(test_url, proxies=proxies, headers=headers)

        if 'you have been blocked' not in res1.text.lower():
            print(f"Proxy {proxy} did not block access (requests).")
    except Exception as e:
        print(f"Error with proxy {proxy} using requests: {e}")

    try:
        scraper = cfscrape.create_scraper()
        scraper.headers.update(headers)
        res = scraper.get(test_url, proxies=proxies)

        if 'you have been blocked' not in res.text.lower():
            print(f"Proxy {proxy} did not block access.")
    except Exception as e:
        print(f"Error with proxy {proxy}: {e}")
