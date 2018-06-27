import random
import requests


def is_valid_ip(*ip):
    """Taken from mirai source"""
    if ip[0] == 127: return False # 127.0.0.0/8 - Loopback
    if ip[0] == 0: return False # 0.0.0.0/8        - Invalid address space
    if ip[0] == 3: return False # 3.0.0.0/8        - General Electric Company
    if ip[0] == 15 or ip[0] == 16: return False # 15.0.0.0/7       - Hewlett-Packard Company
    if ip[0] == 56: return False # 56.0.0.0/8       - US Postal Service
    if ip[0] == 10: return False # 10.0.0.0/8       - Internal network
    if ip[0] == 192 and ip[1] == 168: return False # 192.168.0.0/16   - Internal network
    if ip[0] == 172 and ip[1] >= 16 and ip[1] < 32: return False # 172.16.0.0/14    - Internal network
    if ip[0] == 100 and ip[1] >= 64 and ip[1] < 127: return False # 100.64.0.0/10    - IANA NAT reserved
    if ip[0] == 169 and ip[1] > 254: return False # 169.254.0.0/16   - IANA NAT reserved
    if ip[0] == 198 and ip[1] >= 18 and ip[2] < 20: return False # 198.18.0.0/15    - IANA Special use
    if ip[0] >= 224: return False # 224.*.*.*+       - Multicast
    if ip[0] in (6, 7, 11, 21, 22, 26, 28, 29, 30, 33, 55, 214, 215): return False # Department of Defense
    return True


def ip_to_string(*ip):
    return "%s.%s.%s.%s" % ip


def get_random_ip():
    while True:
        ip = tuple(random.randrange(256) for i in range(4))

        if is_valid_ip(*ip):
            return ip


def get_random_ip_string():
    return ip_to_string(*get_random_ip())


def get_random_homepage():
    for count in range(1000):
        ip = get_random_ip()
        url = "http://%s" % ip_to_string(*ip)
        print(url)
        try:
            res = requests.get(url, timeout=.2)
        except (requests.ConnectTimeout, requests.ConnectionError):
            continue
        print(url, res.status_code, res.content)
        if res.status_code == 200:
            return ip_to_string(*ip)
    return None


if __name__ == "__main__":

    print(get_random_homepage())
