"""
/***************************************************************************
 *
 * Copyright (c) 2015 Baidu.com, Inc. All Rights Reserved
 *
 **************************************************************************/



/**
 * @file fetcher.py
 * @author zhangruiqing01(zhangruiqing01@baidu.com)
 * @date 2015/08/31 10:20:38
 * @version $Revision$
 * @brief
 *

 **/

"""
import urllib2
from HTMLParser import HTMLParser
import urlparse

class MyHTMLParser(HTMLParser):
    """
    encapsulate HTMLParser, for fetching specific content
    """
    def __init__(self):
        HTMLParser.__init__(self)
        self.links = []
        self.figures = []
        self.href = 0

    def append_link(self, url):
        if url.startswith('http://'):
            self.links.append(url)

    def handle_starttag(self, tag, attrs):
        if tag == 'a' or tag == 'link':
            for name, value in attrs:
                if name == "href":
                    self.append_link(value)
        if tag == 'img' or tag == 'script':
            for name, value in attrs:
                if name == "src":
                    self.append_link(value)

    def get_urls(self):
        """
        :return: links of sub-pages
        """
        return self.links

    def get_figures(self):
        """
        :return: figures src current page
        """

