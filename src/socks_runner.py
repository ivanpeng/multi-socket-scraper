
from __future__ import division
import httplib
import socks
import urllib2
from Queue import Queue
from threading import Thread, Condition, Lock
from threading import active_count as threading_active_count
from get_reviews import CanadianTireReviews

import time
import random

"""

https://gist.github.com/869791

SocksiPy + urllib handler

version: 0.2
author: e

This module provides a Handler which you can use with urllib2 to allow it to tunnel your connection through a socks.sockssocket socket, without monkey patching the original socket...
"""

class SocksiPyConnection(httplib.HTTPConnection):
    def __init__(self, proxytype, proxyaddr, proxyport = None, rdns = True, username = None, password = None, *args, **kwargs):
        self.proxyargs = (proxytype, proxyaddr, proxyport, rdns, username, password)
        httplib.HTTPConnection.__init__(self, *args, **kwargs)

    def connect(self):
        self.sock = socks.socksocket()
        self.sock.setproxy(*self.proxyargs)
        if isinstance(self.timeout, float):
            self.sock.settimeout(self.timeout)
        self.sock.connect((self.host, self.port))

class SocksiPyHandler(urllib2.HTTPHandler):
    def __init__(self, *args, **kwargs):
        self.args = args
        self.kw = kwargs
        urllib2.HTTPHandler.__init__(self)

    def http_open(self, req):
        def build(host, port=None, strict=None, timeout=0):
            conn = SocksiPyConnection(*self.args, host=host, port=port, strict=strict, timeout=timeout, **self.kw)
            return conn
        return self.do_open(build, req)

class Monitor(Thread):
    def __init__(self, queue, discovery):
        Thread.__init__(self)
        self.queue = queue
        self.discovery = discovery
        self.finish_signal = False

    def finish(self):
        self.finish_signal = True

    def run(self):
        while not self.finish_signal:
            time.sleep(5)
            print "Elements in Queue:", self.queue.qsize(), "Active Threads:", threading_active_count(), "Exceptions Counter:", self.discovery.exception_counter

class Worker(Thread):
    def __init__(self, queue, discovery, socks_proxy_port):
        Thread.__init__(self)
        self.queue = queue
        self.discovery = discovery
        self.socks_proxy_port = socks_proxy_port
        self.opener = urllib2.build_opener(SocksiPyHandler(socks.PROXY_TYPE_SOCKS4, 'localhost', self.socks_proxy_port))
        self.ctr = CanadianTireReviews(prodsPath="prodsList.txt", revsPath = "/home/ivan/temp/revsList.txt")

    def get_url(self, url):
        try:
            #h = urllib2.urlopen(url)
            h = self.opener.open(url)

            return h.getcode()

        except urllib2.URLError, e:
            return e.code

    def run(self):
        while True:
            try:
                item = self.queue.get()

                if item == None:
                    self.queue.put(None) # Notify the next worker
                    break

                # Grab url from queue; no need to have index
                url = str(item)

                #code = self.get_url(url)
                # Now process the html code with beautiful soup and write out to file
                
                self.ctr.writeRevs(url)

                self.discovery.lock.acquire()
                self.discovery.records_to_process -= 1
                if self.discovery.records_to_process == 0:
                    self.discovery.lock.notify()
                self.discovery.lock.release()

            except (socks.Socks4Error, httplib.BadStatusLine), e:
                # TypeError: 'Socks4Error' object is not callable
                print e
                self.discovery.exception_counter_lock.acquire()
                self.discovery.exception_counter += 1
                self.discovery.exception_counter_lock.release()
                pass # leave this element for the next cycle

            i = random.randrange(0,100)/31
            time.sleep(1.5 + i)
            

class Croupier(Thread):
    Base = 0
    Top = 25000000
    #Top = 1000
    def __init__(self, queue, discovery):
        Thread.__init__(self)
        self.finish_signal = False
        self.queue = queue
        self.discovery = discovery
        self.discovery.records_to_process = 0

    def run(self):
        # General algorithm here: add items to self.queue

        while True:
            items = []
            with open('prodList.txt', 'r') as f:
                # Here, add every url to the queue
                items = [line.strip() for line in f]

            
            self.discovery.records_to_process = len(items)

            if self.discovery.records_to_process == 0:
                break

            for item in items:
                self.queue.put(item)

            # Wait until the last item is updated on the db
            self.discovery.lock.acquire()
            while self.discovery.records_to_process != 0:
                self.discovery.lock.wait()
            self.discovery.lock.release()

#            time.sleep(5)

        # Send a 'signal' to workers to finish
        self.queue.put(None)

    def finish(self):
        self.finish_signal = True

class Discovery:
    NWorkers = 45
    SocksProxyBasePort = 9050
    Contention = 10000

    def __init__(self):
        self.queue = Queue(Discovery.Contention)
        self.workers = []
        self.lock = Condition()
        self.exception_counter_lock = Lock()
        self.records_to_process = 0
        self.exception_counter = 0

    def start(self):
        croupier = Croupier(self.queue, self)
        croupier.start()

        for i in range(Discovery.NWorkers):
            worker = Worker(self.queue, self, Discovery.SocksProxyBasePort + i)
            self.workers.append(worker)

        for w in self.workers:
            w.start()

        monitor = Monitor(self.queue, self)
        monitor.start()

        for w in self.workers:
            w.join()

        croupier.join()

        print "Queue finished with:", self.queue.qsize(), "elements"

        monitor.finish()

def main():
    discovery = Discovery()
    discovery.start()

if __name__ == '__main__':
    main()

#
# MISC NOTES
#
# - How many IMDB ratings pages are currently indexed by Google? query: inurl:www.imdb.com/user/*/ratings
# - [pymongo] cursor id '239432858681488351' not valid at server Options: http://groups.google.com/group/mongodb-user/browse_thread/thread/4ed6e3d77fb1c2cf?pli=1
#     That error generally means that the cursor timed out on the server -
#     this could be the case if you are performing a long running operation
#     while iterating over the cursor. The best bet is probably to turn off
#     the timeout by passing "timeout=False" in your call to find:
