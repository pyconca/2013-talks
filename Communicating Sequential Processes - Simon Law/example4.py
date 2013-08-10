#!/usr/bin/env python3

import multiprocessing
import queue
import re
import sys
import threading
import urllib.request


def urlget(i, o):
    while True:
        url, depth, maxdepth = i.get()
        with urllib.request.urlopen(url) as response:
            content = response.read()
        o.put((url, content))

        if depth < maxdepth:
            match = re.search(r'href="(/\w.*?)"', content.decode('utf-8'))
            if match:
                i.put((url + match.group(1), depth + 1, maxdepth))

        i.task_done()


def download(urls):
    i, o = queue.Queue(), queue.Queue()
    for _ in range(multiprocessing.cpu_count()):
        thread = threading.Thread(target=urlget, args=(i, o), daemon=True)
        thread.start()

    for url in urls:
        i.put((url, 0, 1))

    while i.unfinished_tasks > 0 or not o.empty():
        yield o.get()


if __name__ == '__main__':
    contents = download(sys.argv[1:])
    for url, content in contents:
        print("{}: {}".format(url, content[:50]))


# time ./example4.py http://2013.pycon.ca http://500px.com http://chango.com http://kontagent.com http://rackspace.com
