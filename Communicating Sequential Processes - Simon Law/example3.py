#!/usr/bin/env python3

import multiprocessing
import queue
import sys
import threading
import urllib.request


def urlget(i, o):
    while True:
        url = i.get()
        with urllib.request.urlopen(url) as response:
            o.put((url, response.read()))
        i.task_done()


def download(urls):
    i, o = queue.Queue(), queue.Queue()
    for _ in range(multiprocessing.cpu_count()):
        thread = threading.Thread(target=urlget, args=(i, o), daemon=True)
        thread.start()

    for url in urls:
        i.put(url)

    while i.unfinished_tasks > 0 or not o.empty():
        yield o.get()


if __name__ == '__main__':
    contents = download(sys.argv[1:])
    for url, content in contents:
        print("{}: {}".format(url, content[:50]))


# time ./example3.py http://2013.pycon.ca http://500px.com http://chango.com http://kontagent.com http://rackspace.com
