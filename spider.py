"""
/***************************************************************************
 *
 * Copyright (c) 2015 Baidu.com, Inc. All Rights Reserved
 *
 **************************************************************************/



/**
 * @file mini_spider.py
 * @author zhangruiqing01(zhangruiqing01@baidu.com)
 * @date 2015/08/28 16:24:50
 * @version $Revision$
 * @brief
 *
 **/
"""
from __future__ import with_statement
from ConfigParser import ConfigParser
import os
import logging
import Queue
import fetcher
import logging as log
import hashlib
import time
import threading
import re
import urllib
import MyHtmlParser

class MiniSpider(object):
    """
    MiniSpider: the outmost class that crawl pages
    """
    def __init__(self, configure):
        self._url_list = configure.get("spider", "url_list_file")
        self._output_dir = configure.get("spider", "output_directory")
        self._max_depth = int(configure.get("spider", "max_depth"))
        self._interval = int(configure.get("spider", "crawl_interval"))
        self._timeout = int(configure.get("spider", "crawl_timeout"))
        self.fetch_pattern = configure.get("spider", "target_url")
        self.fig_pattern = re.compile(self.fetch_pattern)
        self._thread_count = int(configure.get("spider", "thread_count"))
        self._url_queue = Queue.Queue()
        self._url_visited = [] # need to be synchronized among threads
        self._lock = threading.Lock()
        self.init_urls()
        if not os.path.exists(self._output_dir):
            os.makedirs(self._output_dir)

        self._thread_list = []

    def init_urls(self):
        """
        Initialize the _url_queue and _url_visited
        :return:None
        """
        init_depth = 1
        with open(self._url_list) as url_file:
            for line in url_file:
                line = line.strip()
                try:
                    if line not in self._url_visited:
                        self._url_queue.put([line, init_depth], timeout=1)
                        self._url_visited.append(line)
                except Queue.Full as e:
                    log.warn(e)
                    pass

    def fetch(self, thread_id):
        """
        Fetch according to BFS with _url_queue
        :return: None
        """
        #log.info("Running thread %s" % threading.current_thread())
        #print "Running thread", threading.current_thread()
        log.info("Running thread %s" % thread_id)
        while True:
            time.sleep(self._interval)
            try:
                cur_url, cur_depth = self._url_queue.get(timeout=1)
                cur_url = cur_url.strip()
            except Queue.Empty as e:
                log.warn(e)
                continue

            # check whether this url is a figure
            if self.fig_pattern.match(cur_url):
                log.info(str(thread_id) + " - downloading: %s" % cur_url)
                fig_suffix = cur_url[cur_url.rindex("."):]
                file_name = "%s%s" % (hashlib.md5(cur_url).hexdigest(), fig_suffix)
                file_path = os.path.join(self._output_dir, file_name)
                urllib.urlretrieve(cur_url, file_path)
            elif cur_depth <= self._max_depth:
                # get content of this page
                fetch_tool = fetcher.Fetcher(cur_url,
                                             self._output_dir,
                                             self._timeout)
                content = fetch_tool.read_content(thread_id)
                if content is None or len(content) == 0:
                    continue

                # get sub-page urls
                sub_urls = fetch_tool.get_sub_urls(content)
                if sub_urls is None:
                    continue
                for item in sub_urls:
                    with self._lock:  # lock _url_visited, check
                        if item in self._url_visited:
                            continue
                    try:
                        with self._lock:  # lock _url_visited, add
                            self._url_visited.append(item)
                        self._url_queue.put([item, cur_depth + 1], timeout=1)
                    except Queue.Full as e:
                        log.warn(e)
                        break

            self._url_queue.task_done()

    def multi_thread(self):
        """
        Fetch pages by multi-thread
        :return:
        """
        for i in xrange(self._thread_count):
            single_thread = threading.Thread(target = self.fetch, args = (str(i)))
            self._thread_list.append(single_thread)
            single_thread.setDaemon(True)
            single_thread.start()

        # wait for all tasks until finished
        self._url_queue.join()

        ## stop all spiders
        #for t in self._thread_list:
        #    t.join(self._timeout)
        log.info("mini spider finished")

if __name__ == "__main__":
    config = ConfigParser()
    #config.readfp(sys.argv[1])
    config.readfp(open("a.conf", 'r'))

    # initialize logging
    LOG_LEVEL = logging.DEBUG
    logging.basicConfig(level=LOG_LEVEL,
            format="%(levelname)s:%(name)s:%(funcName)s->%(message)s",  #logging.BASIC_FORMAT,
            datefmt='%a, %d %b %Y %H:%M:%S', filename='spider.log', filemode='a')

    spider = MiniSpider(config)
    spider.multi_thread()
