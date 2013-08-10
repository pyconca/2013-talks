#!/usr/bin/env python3

import bs4
import multiprocessing
import queue
import sys
import threading
import urllib.request


def pipeline(target, i):
    o = queue.Queue()

    for _ in range(multiprocessing.cpu_count()):
        thread = threading.Thread(target=target, args=(i, o), daemon=True)
        thread.start()

    return o


def urlget(i, o):
    while True:
        url = i.get()
        with urllib.request.urlopen(url) as response:
            content = response.read()
        o.put((url, content))
        i.task_done()


def extract(i, o):
    while True:
        url, content = i.get()
        soup = bs4.BeautifulSoup(content)
        links = [tag.attrs.get('src', '') for tag in soup.find_all('img')]
        o.put((url, links))
        i.task_done()


def extract_images(urls):
    i = queue.Queue()
    q = pipeline(urlget, i)
    o = pipeline(extract, q)

    for url in urls:
        i.put(url)

    while i.unfinished_tasks > 0 or q.unfinished_tasks > 0 or not o.empty():
        yield o.get()


if __name__ == '__main__':
    contents = extract_images(sys.argv[1:])
    for url, digest in contents:
        print("{}: {}".format(url, digest[:8]))


# time ./example7.py http://2013.pycon.ca http://500px.com http://chango.com http://kontagent.com http://rackspace.com
