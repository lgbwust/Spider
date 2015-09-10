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

import unittest
import fetcher
import urllib2
import StringIO
import gzip


class TestFetcher(unittest.TestCase):
    """
    Unittest of Fetcher
    """
    def setUp(self):
        self.timeout = 1
        self.fetch_tool = fetcher.Fetcher("http://www.baidu.com", 'output', timeout=self.timeout)

    def test_check_url(self):
        url = "http:/www.baidu.com"
        self.assertEquals(self.fetch_tool.check_url(url), False)

        url = "http://ftp.baidu.com"
        self.assertEquals(self.fetch_tool.check_url(url), True)

        url = "http://https.baidu.com"
        self.assertEquals(self.fetch_tool.check_url(url), True)

    def test_enc_dec(self):
        url = "http://www.baidu.com"
        response = urllib2.urlopen(url, timeout = self.timeout)
        urllib2.urlopen
        if response.info().get('Content-Encoding',"") == 'gzip':  #e.g www.sina.com.cn
            buf = StringIO.StringIO(response.read())
            f = gzip.GzipFile(fileobj=buf)
            content = f.read()
        else:
            content = response.read()
        content_len = len(self.fetch_tool.enc_dec(content))
        self.assertNotEqual(content_len, 0)

if __name__ == '__main__':
    unittest.main()
