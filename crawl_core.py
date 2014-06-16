import urllib2
import re
import os
import ConfigParser
import gzip
from StringIO import StringIO

from mongodb import CrawlDB


class Crawl(object):
    '''The base class of all the other crawl'''
    def __init__(self, conf_session, page_host, level, filter_level):
        conf_file = 'setting.cfg'
        self.page_host = page_host
        self.level = level
        self.filter_level = filter_level
        crawl_cf = ConfigParser.ConfigParser()
        assert os.path.exists(conf_file)
        crawl_cf.read(conf_file)
        self.user_agent= crawl_cf.get('header', 'User-Agent')
        self.html_file_dir = crawl_cf.get(conf_session, 
                                          ''.join(['LEVEL', str(self.level), '_PATH']))
        self.page_rule = crawl_cf.get(conf_session, 
                                      ''.join(['LEVEL', str(self.filter_level)]))
        
    def crawl_page(self, url_coll_name):
        '''Download the web page, store tha page in a file and return the file path.'''
        db_html_downloaded = CrawlDB()
        url = db_html_downloaded.db_read(url_coll_name, self.level, self.level)
        if not url:
            return False
        if not os.path.isdir(self.html_file_dir):
            os.makedirs(self.html_file_dir)
        self.data_file = os.path.join(self.html_file_dir, url.split('/')[-1])
        headers = { 'Accept-encoding' : 'gzip', 
                    'User-Agent' : self.user_agent,
                    'Host' : self.page_host }
        crawl_res = urllib2.Request(url, None, headers)
        
        try:
            crawl_rep = urllib2.urlopen(crawl_res)
        except urllib2.HTTPError, e:
            return False
        except urllib2.URLError, e:
            return False
        else:
            if crawl_rep:
                if crawl_rep.info().get('Content-Encoding') == 'gzip':
                    crawl_rep = gzip.GzipFile(fileobj=StringIO(crawl_rep.read()))
                save_page = crawl_rep.readlines()
                with open(self.data_file, 'w') as f:
                    f.writelines(save_page)
                return self.data_file
            else:
                return False
                
    def crawl_filter(self, file_coll_name):
        '''With the regexp rule according the page level, 
        filter web page to return a list of the destination strings
        '''
        db_html_analysed = CrawlDB()
        page_re = re.compile(self.page_rule)
        page_filter = []
        html_file_path = db_html_analysed.db_read(file_coll_name, 
                                                  self.level, 
                                                  self.filter_level)
        if not html_file_path:
            return False
        if os.path.isfile(html_file_path):
            with open(html_file_path, 'r') as f:
                for line in f:
                    match_obj = re.findall(page_re, line)
                    if match_obj:
                        page_filter.extend(match_obj)
            return page_filter
        else:
            return False