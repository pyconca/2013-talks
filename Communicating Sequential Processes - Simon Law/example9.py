#!/usr/bin/env python3

import bs4
import multiprocessing
import sys
import urllib.request


def pipeline(target, i):
    o = multiprocessing.JoinableQueue()

    for _ in range(multiprocessing.cpu_count()):
        proc = multiprocessing.Process(target=target, args=(i, o),
                                       daemon=True)
        proc.start()

    return o

shared = multiprocessing.Manager()
urlcache = shared.dict()


def urlget(i, o):
    while True:
        url = i.get()

        content = urlcache.get(url, None)
        if content is None:
            with urllib.request.urlopen(url) as response:
                content = response.read()
            urlcache[url] = content

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
    i = multiprocessing.JoinableQueue()
    q = pipeline(urlget, i)
    o = pipeline(extract, q)

    for url in urls:
        i.put(url)

    while (not i._unfinished_tasks._semlock._is_zero() or
           not i._unfinished_tasks._semlock._is_zero() or
           not o.empty()):
        yield o.get()


if __name__ == '__main__':
    contents = extract_images(sys.argv[1:])
    for url, digest in contents:
        print("{}: {}".format(url, digest[:8]))


# time ./example9.py http://2013.pycon.ca http://500px.com http://chango.com http://kontagent.com http://rackspace.com
