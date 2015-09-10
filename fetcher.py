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

import urllib
import socket
import re
import logging as log
import MyHtmlParser
import chardet
from threading import Timer
import urllib2
import StringIO
import gzip

class Fetcher:
    """
    Implement fetching functions of single thread
    """
    def __init__(self, url, output, timeout):
        self.url = url
        self.output_dir = output
        self.timeout = timeout

    def check_url(self, url):
        """
        check whether a url is valid
        :param url: given page url
        :return: True(valid) / False(invalid)
        """
        url_format = '(http|ftp|https):\/\/[\w\-_]+(\.[\w\-_]+)+([\w\-\.,@?^=%&amp;:/~\+#]*[\w\-\@?^=%&amp;/~\+#])?'
        url_pattern = re.compile(url_format)
        if url_pattern.match(url):
            return True
        return False

    def enc_dec(self, content):
        """
        decode the given content into utf-8
        :param content: the given content
        :return: the decoded content in utf-8
        """
        try:
            encoding_dict = chardet.detect(content)
            web_encoding = encoding_dict['encoding']
            if web_encoding is not None:
                if web_encoding.lower() == 'utf-8':
                    return content
                else:
                    return content.decode('web_encoding', 'ignore').encode('utf-8')
            else:
                return content
        except Exception as e:
            log.warn('encode detection error %s' % e)
            return content

    def check_url(self, url):
        """
        check whether a url is valid
        :param url: given page url
        :return: True(valid) / False(invalid)
        """
        url_format = '(http|ftp|https):\/\/[\w\-_]+(\.[\w\-_]+)+([\w\-\.,@?^=%&amp;:/~\+#]*[\w\-\@?^=%&amp;/~\+#])?'
        url_pattern = re.compile(url_format)
        if url_pattern.match(url):
            return True
        return False

    def read_content(self, thread_id):
        """
        get the content of a page
        :return: content (string)
        """
        log.info(str(thread_id) + " - getting url: %s" % self.url)
        content = ''

        try:
            response = urllib2.urlopen(self.url, timeout = self.timeout)
            if response.info().get('Content-Encoding',"") == 'gzip':  #e.g www.sina.com.cn
                buf = StringIO.StringIO(response.read())
                f = gzip.GzipFile(fileobj=buf)
                content = f.read()
            else:
                content = response.read()
            content = self.enc_dec(content)
            return content
        except socket.timeout:
            log.warn("Timeout in fetching %s" % self.url)
        except urllib2.HTTPError as e:
            log.warn("error in fetching content of %s: %s" % (self.url, e))
            return content
        except urllib2.URLError as e:
            log.warn("error in fetching content of %s: %s" % (self.url, e))
            return content
        except socket.gaierror as e:
            log.warn("error in fetching content of %s: %s" % (self.url, e))
            return content

    def get_sub_urls(self, content):
        """
        return the sub-page urls given content of current page
        :param content: content of current page
        :return: a list containing all sub-page urls
        """

        if not self.check_url(self.url):
            return []
        sub_urls = []
        html_parser = MyHtmlParser.MyHTMLParser()
        if content is not None:
            try:
                html_parser.feed(content)
                for item in html_parser.get_urls():
                    if self.check_url(item):
                        sub_urls.append(item)
            except Exception as e:
                log.warn("Error in getting subpage of %s: %s" % (self.url, e))
                return sub_urls

            return sub_urls
