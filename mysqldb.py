import os.path
import pymysql
import ConfigParser


class CrawlDB(object):
    '''Offer methods to read and write the crawl datas to mysql database'''
    def __init__(self):
        conf_file = "setting.cfg"
        mysql_db_cf = ConfigParser.ConfigParser()
        assert os.path.exists(conf_file)
        mysql_db_cf.read(conf_file)
        self.host = mysql_db_cf.get("mysqldb", "DB_HOST")
        self.port = int(mysql_db_cf.get("mysqldb", "DB_PORT"))
        self.db_name = mysql_db_cf.get("mysqldb", "DB_NAME")
        
    def db_connect(func):
        '''Decorated method for connection building and releasing of mysql database.'''
        def _db_connect(self, *args, **kwargs):
            self.db_conn = pymysql.connect(host = self.host, 
                                           port = self.port, 
                                           user = "root", 
                                           passwd="", 
                                           db = self.db_name)
            func_result = func(self, *args, **kwargs)
            self.db_conn.close()
            return func_result
        return _db_connect
    
    @db_connect
    def db_write(self, tbl_name, path, level, currentlv_excuted, nextlv_excuted):
        '''A method write a record to the mysql database.
        If the path exists, then do nothing except a log infomation.
        '''
        w_cur = self.db_conn.cursor()
        r_sql_comm = "SELECT path FROM %s WHERE path = '%s' " % (tbl_name, path)
        if w_cur.execute(r_sql_comm):
            return False
        w_sql_comm = "INSERT INTO %s(path, level, currentlv_excuted, nextlv_excuted) \
                      VALUES('%s', %s, %s, %s)" % (tbl_name, 
                                                   path, level, 
                                                   currentlv_excuted, 
                                                   nextlv_excuted)
        if w_cur.execute(w_sql_comm):
            self.db_conn.commit()
            w_cur.close()
            return True
        else:
            w_cur.close()
            return False

    @db_connect
    def db_read(self, db_tbl_name, db_level, db_filter_level):
        '''A method read an unexcuted record from mysql database.
        Once the reading action done, increase the value of the 
        currentlv_excuted or nextlv_excuted by 1.
        '''
        if db_level == db_filter_level:
            excuted_name = "currentlv_excuted"
        else:
            excuted_name = "nextlv_excuted"
        r_cur = self.db_conn.cursor(pymysql.cursors.DictCursor)
        r_sql_comm = "SELECT path FROM %s WHERE level = %s AND %s = 0 \
                      LIMIT 1" % (db_tbl_name, db_level, excuted_name)
        if not r_cur.execute(r_sql_comm):
            r_cur.close()
            return False
        fetch_item = r_cur.fetchone()
        if fetch_item is None:
            r_cur.close()
            return False
        else:
            w_sql_comm = "UPDATE %s SET %s = %s + 1 \
                          WHERE path = '%s'" % (db_tbl_name, 
                                                excuted_name, 
                                                excuted_name, 
                                                fetch_item["path"])
            if not r_cur.execute(w_sql_comm):
                r_cur.close()
                return False
            else:
                self.db_conn.commit()
                r_cur.close()
                return fetch_item["path"]
                
class DBItemCreate(object):
    '''Construct a new record and write it to the mysql database.
    Set the currentlv_excuted and nextlv_excuted to 0. 
    '''
    def __init__(self, level, path, item_type):
        self.db = CrawlDB()
        self.coll_name = item_type
        self.level = level
        self.path = path
        
    def write2db(self):
        if self.db.db_write(self.coll_name, 
                            self.path, 
                            self.level, 
                            0, 
                            0):
            return True
        else:
            return False
 
 
if __name__ == '__main__':
    test_item = DBItemCreate(0, 
                               'http://tieba.baidu.com/f?kw=%C3%C0%C5%AE&fr=ala1', 
                               'tieba_url')
    test_item2 = DBItemCreate(2, 
                                'html_file/level2/3003671238', 
                                'tieba_file')
    test_item3 = DBItemCreate('2', 
                                'http://imgsrc.baidu.com/forum/w%3D580%3B/\
                                sign=e713c6e39058d109c4e3a9bae163cdbf/\
                                c9fcc3cec3fdfc03a8024625d63f8794a4c22631.jpg', 
                                'tieba_url')
    print test_item.write2db(), test_item2.write2db(), test_item3.write2db() 
    test_db = CrawlDB()
    print test_db.db_read('tieba_url', 0, 0)