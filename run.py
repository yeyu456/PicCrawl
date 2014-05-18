import os.path
import ConfigParser
import time
import cProfile

from mongodb import DBItemCreate
from crawl_spec.tieba_crawl import TiebaThread, TiebaProcess


class CrawlRun(object):
    def __init__(self, page_host):
        conf_file = 'setting.cfg'
        run_cf = ConfigParser.ConfigParser()
        assert os.path.exists(conf_file)
        run_cf.read(conf_file)
        seed_url = run_cf.get(page_host, 'SEED0')
        seed_url_coll_name = run_cf.get(page_host, 'url_coll_name')
        seed_init = DBItemCreate(0, seed_url, seed_url_coll_name)
        seed_init.write2db()
        
        self.crawl_d_thread = run_cf.items('Download Thread')
        self.crawl_a_thread = run_cf.items('Analyse Thread')
    
    def t_run(self):
        '''MultiThread type of crawl method.'''
        test_list = []
        lv_num = 3
        for n in range(lv_num):
            d = int(self.crawl_d_thread[n][1])
            test_list.extend([TiebaThread(True, n, n) for num in range(d)])
            if n != (lv_num - 1): #while n isn't the bottom level number, analyse the html file 
                a = int(self.crawl_a_thread[(n * 2)][1])  # The thread number of method that get level n url from level n html file  
                a2 = int(self.crawl_a_thread[(n * 2 + 1)][1]) # The thread number of method that get level n+1 url from level n html file  
                test_list.extend([TiebaThread(False, n, n) for num in range(a)])
                test_list.extend([TiebaThread(False, n, (n + 1)) for num in range(a2)])
            
        for n in test_list:
            n.start()
            
    def p_run(self):
        '''MultiProcess type of crawl method.'''
        test_list = []
        lv_num = 3
        for n in range(lv_num):
            d = int(self.crawl_d_thread[n][1])
            test_list.extend([TiebaProcess(True, n, n) for num in range(d)])
            if n != (lv_num - 1): #while n isn't the bottom level number, analyse the html file 
                a = int(self.crawl_a_thread[(n * 2)][1])  # The process number of method that get level n url from level n html file  
                a2 = int(self.crawl_a_thread[(n * 2 + 1)][1]) # The process number of method that get level n+1 url from level n html file  
                test_list.extend([TiebaProcess(False, n, n) for num in range(a)])
                test_list.extend([TiebaProcess(False, n, (n + 1)) for num in range(a2)])
            
        for n in test_list:
            n.start()
                
if __name__ == '__main__':
    t = CrawlRun('tieba.baidu.com')
    t.p_run()