import argparse
import queue
import sys

from bs4 import BeautifulSoup

import requests


def parse_params():
    parser = argparse.ArgumentParser()
    parser.add_argument("-u", "--url", dest="url", help="url")

    return parser.parse_args().url


def process_origin(origin):
    if origin is None:
        print('usage: crawl.py [-h] [-u URL]')
        sys.exit(1)
    print(origin)
    if not origin.startswith('http://') and not origin.startswith('https://'):
        return 'http://' + origin
    return origin


def fetch_page(page):
    request = requests.get(page)
    soup = BeautifulSoup(request.text, 'html.parser')
    return soup, request.status_code


def scan_page(page, origin, q, checked_page, used_links):
    soup, code = fetch_page(page)
    checked_page.append(page)

    for link in soup.find_all('a'):
        link = link.get('href')
        if link:
            if link.startswith('/') and page.endswith('/'):
                new_link = page + link[1:]
            elif link.startswith('/'):
                new_link = origin + link
            elif link.startswith(origin):
                new_link = link
            else:
                new_link = False
                continue

            if new_link and new_link not in used_links:
                print("new link", new_link)
                q.put(new_link)
                used_links.append(new_link)
    return code


def start_scan(origin):
    q = queue.Queue(maxsize=0)
    checked_page = []
    used_links = []
    error_pages = {}

    q.put(origin, True)
    while not q.empty():
        print("Queue size:", q.qsize())
        url = q.get(True)
        print("Checking URL:", url)
        if url not in checked_page:
            code = scan_page(url, origin, q, checked_page, used_links)
            if not code == 200:
                print(code, "received from:", url)
                error_pages[url] = code

    q.task_done()
    return error_pages


def report(errors):
    print("Errors:")
    for url, code in errors.items():
        print("Status Code:", code, "- URL:", url)


def main():
    origin = parse_params()
    origin = process_origin(origin)
    errors = start_scan(origin)
    report(errors)

main()
