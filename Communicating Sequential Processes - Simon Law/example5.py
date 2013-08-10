#!/usr/bin/env python3

import hashlib
import multiprocessing
import queue
import re
import sys
import threading
import urllib.request


def urlget(i, o):
    while True:
        url = i.get()
        with urllib.request.urlopen(url) as response:
            content = response.read()
        o.put((url, content))
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


def hasher(i, o):
    while True:
        url, content = i.get()
        o.put((url, hashlib.sha512(content).hexdigest()))
        i.task_done()


def hash_urls(urls):
    i, o = queue.Queue(), queue.Queue()
    for _ in range(multiprocessing.cpu_count()):
        thread = threading.Thread(target=hasher, args=(i, o), daemon=True)
        thread.start()

    for url, content in download(urls):
        i.put((url, content))

    while i.unfinished_tasks > 0 or not o.empty():
        yield o.get()


if __name__ == '__main__':
    contents = hash_urls(sys.argv[1:])
    for url, digest in contents:
        print("{}: {}".format(url, digest[:8]))


# time ./example5.py http://2013.pycon.ca http://500px.com http://chango.com http://kontagent.com http://rackspace.com
