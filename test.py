#!/usr/bin/env python
import ConfigParser
import os
import re
cf = ConfigParser.ConfigParser()

if os.path.isfile("BG_Pic_Crawl/setting.cfg"):
    cf.read("BG_Pic_Crawl/setting.cfg")
#    a = cf.get('tieba.baidu.com', 'LEVEL0')
    a = r'<a href="/f\?kw=(?:%\w{2})+&pn=\d+">\d+</a>'
    match_obj = re.findall(a, '<a href="/f?kw=%CE%E4%B6%AF%C7%AC%C0%A4&pn=50">2</a> ')
    for n in match_obj:
        print n
else:
    print 'error'
