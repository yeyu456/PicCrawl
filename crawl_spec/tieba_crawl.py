import urllib2
import re
import threading
import time
import os.path
import ConfigParser
import multiprocessing

from crawl_core import Crawl
from mongodb import DBItemCreate


class TiebaDownload(Crawl):
    '''Download the Tieba url, store the web page in a file 
    and insert a record into database.
    '''
    def __init__(self, level):
        conf_file = 'setting.cfg'
        self.main_page = 'tieba.baidu.com'
        self.level = level
        TiebaDownload_cf = ConfigParser.ConfigParser()
        assert os.path.exists(conf_file)
        TiebaDownload_cf.read(conf_file)
        self.host = TiebaDownload_cf.get(self.main_page, 
                                         ''.join(['LEVEL', str(self.level), '_HOST']))
        self.tieba_url_coll_name = TiebaDownload_cf.get(self.main_page, 
                                                        'url_coll_name')
        self.tieba_file_coll_name = TiebaDownload_cf.get(self.main_page, 
                                                         'file_coll_name')
        super(TiebaDownload, self).__init__(self.main_page, 
                                            self.host, 
                                            self.level, 
                                            self.level) 
        
    def download(self):
        download_file_path = super(TiebaDownload, self).crawl_page(self.tieba_url_coll_name)
        if download_file_path:
            tieba_file_mongo_item = DBItemCreate(self.level, 
                                                 download_file_path, 
                                                 self.tieba_file_coll_name)
            tieba_file_mongo_item.write2db()
            return True
        else:
            return False

            
class TiebaAnalyse(Crawl):
    '''Analyse the Tieba web page to get the url with the regexp rule, 
    then insert a record into database.
    '''
    def __init__(self, level, analyse_level):
        conf_file = 'setting.cfg'
        self.main_page = 'tieba.baidu.com'
        self.level = level
        self.analyse_level = analyse_level
        TiebaAnalyse_cf = ConfigParser.ConfigParser()
        assert os.path.exists(conf_file) 
        TiebaAnalyse_cf.read(conf_file)
        self.see_lz_post = TiebaAnalyse_cf.get(self.main_page, 
                                                'SEE_LZ_POST')
        self.host = TiebaAnalyse_cf.get(self.main_page, 
                                        ''.join(['LEVEL', str(self.level), '_HOST']))
        self.tieba_url_coll_name = TiebaAnalyse_cf.get(self.main_page, 
                                                       'url_coll_name')
        self.tieba_file_coll_name = TiebaAnalyse_cf.get(self.main_page, 
                                                        'file_coll_name')
        super(TiebaAnalyse, self).__init__(self.main_page, 
                                           self.host, 
                                           self.level, 
                                           self.analyse_level)
    
    def analyse(self):
        url_prefix = 'http://' + self.main_page
        url_post = ''
        if self.analyse_level == 1:
            url_post = self.see_lz_post
        elif self.analyse_level == 2:
            url_prefix = ''
        else:
            pass
        url_part = super(TiebaAnalyse, self).crawl_filter(self.tieba_file_coll_name)
        if url_part:
            for url in url_part:
                if self.analyse_level == 2:
                    url = url.replace('\\', '') #del the double backslash in some html file.
                tieba_url_mongo_item = DBItemCreate(self.analyse_level, 
                                                    ''.join([url_prefix, url, url_post]), 
                                                    self.tieba_url_coll_name) 
                tieba_url_mongo_item.write2db()
            return True
        else:
            return False
        
class TiebaThread(threading.Thread):
    '''MultiThread class for TiebaDownload and TiebaAnalyse.'''
    def __init__(self, download, t_level, t_analyse_level):
        super(TiebaThread, self).__init__()
        self.download = download
        self.t_level = t_level
        self.t_analyse_level = t_analyse_level
        
    def run(self):
        while True:
            if self.download:
                t_run = TiebaDownload(self.t_level)
                if not t_run.download():
                    time.sleep(0.1)
            else:
                t_run = TiebaAnalyse(self.t_level, self.t_analyse_level)
                if not t_run.analyse():
                    time.sleep(1)
 
class TiebaProcess(multiprocessing.Process):
    '''MultiProcess class for TiebaDownload and TiebaAnalyse.'''
    def __init__(self, download, t_level, t_analyse_level):
        super(TiebaProcess, self).__init__()
        self.download = download
        self.t_level = t_level
        self.t_analyse_level = t_analyse_level
        
    def run(self):
        while True:
            if self.download:
                t_run = TiebaDownload(self.t_level)
                if not t_run.download():
                    time.sleep(0.1)
            else:
                t_run = TiebaAnalyse(self.t_level, self.t_analyse_level)
                if not t_run.analyse():
                    time.sleep(1)

if __name__ == '__main__':
    test_conf_file = 'BG_Pic_Crawl/setting.cfg'
    test_cf = ConfigParser.ConfigParser()
    test_host = 'tieba.baidu.com'
    
    if os.path.exists(test_conf_file):
        test_cf.read(test_conf_file)
        test_url = test_cf.get(test_host, 'SEED0')
        test_url_coll_name = test_cf.get(test_host, 'url_coll_name')
        test_file_coll_name = test_cf.get(test_host, 'file_coll_name')
    
    test_seed_init = DBItemCreate(0, test_url, test_url_coll_name)
    test_seed_init.write2db()
    test_list = []
    test_list = []
    for i in range(1):
        test_list.append(TiebaThread(True, 0, 0))
    for i2 in range(1):
        test_list.append(TiebaThread(False, 0, 0))
    for i6 in range(2):
        test_list.append(TiebaThread(False, 0, 1))  
    for i3 in range(3):
        test_list.append(TiebaThread(True, 1, 1))
    for i5 in range(6):
        test_list.append(TiebaThread(False, 1, 2))
    for i4 in range(4):
        test_list.append(TiebaThread(False, 1, 1))
    for n in test_list:
        n.start()