#!/usr/bin/env python3

import multiprocessing.pool
import sys
import urllib.request


def urlget(url):
    with urllib.request.urlopen(url) as response:
        return url, response.read()


def download(urls):
    threads = multiprocessing.pool.ThreadPool()
    return threads.imap(urlget, urls)


if __name__ == '__main__':
    contents = download(sys.argv[1:])
    for url, content in contents:
        print("{}: {}".format(url, content[:50]))


# time ./example2.py http://2013.pycon.ca http://500px.com http://chango.com http://kontagent.com http://rackspace.com
