import os.path
import pymongo
import ConfigParser


class CrawlDB(object):
    '''Offer methods to read and write the crawl datas to mongo database'''
    def __init__(self):
        conf_file = 'setting.cfg'
        mongo_db_cf = ConfigParser.ConfigParser()
        assert os.path.exists(conf_file)
        mongo_db_cf.read(conf_file)
        self.host = mongo_db_cf.get('mongodb', 'DB_HOST')
        self.port = int(mongo_db_cf.get('mongodb', 'DB_PORT'))
        self.db_name = mongo_db_cf.get('mongodb', 'DB_NAME')
        
    def db_connect(func):
        '''Decorated method for connection building and releasing of mongo database.'''
        def _db_connect(self, *args, **kwargs):
            db_client = pymongo.mongo_client.MongoClient(self.host, self.port)
            try:
                self.db_con = pymongo.database.Database(db_client, self.db_name)
            except pymongo.errors.InvalidName, e:
                return False
            func_result = func(self, *args, **kwargs)
            db_client.close()
            return func_result
        return _db_connect
        
    @db_connect    
    def db_write(self, coll_name, item):
        '''A method write the collection item to mongo database.
        If the item exists, then do nothing except a log infomation.
        '''
        try:
            coll_con = pymongo.collection.Collection(self.db_con, coll_name, True)
        except pymongo.errors.OperationFailure:
            coll_con = pymongo.collection.Collection(self.db_con, coll_name)
        main_key_value = {'path' : item['path']}
        find_result = coll_con.find(main_key_value)
        if find_result.count() != 0:            return False
        else:
            try:
                coll_con.update(main_key_value, {'$set' : item}, True)
            except pymongo.errors.OperationFailure, e:
                return False
        return True    
            
    @db_connect
    def db_read(self, db_coll_name, db_level, db_filter_level):
        '''A method read an unexcuted item from mongo database.
        Once the reading action done, increase the value of the 
        currentlv_excuted or nextlv_excuted by 1.
        '''
        coll_con = pymongo.collection.Collection(self.db_con, db_coll_name)
        filter_key = 'level' + str(db_filter_level) + 'excuted'
        url_list = coll_con.find_one({ '$and' : [ 
                                                 { filter_key : 0 },
                                                 { 'level' : { '$in' : [db_level] } }
                                                 ] 
                                     })
        if url_list:
            try:
                coll_con.update(url_list, { '$inc' : { filter_key : 1 } })
            except pymongo.errors.OperationFailure, e:
                return False
            else:
                return url_list['path']
        else:
            return False


class DBItemCreate(object):
    '''Construct a new document and write it to the mongo database.
    Set the currentlv_excuted and nextlv_excuted to 0. 
    '''
    def __init__(self, level, path, item_type):
        self.db = CrawlDB()
        self.coll_name = item_type
        self.mongodb_item = {}
        self.mongodb_item['level'] = level
        self.mongodb_item['path'] = path
        self.mongodb_item['level' + str(level) + 'excuted'] = 0
        if level == 0 or level == 1:
            self.mongodb_item['level' + str(level + 1) + 'excuted'] = 0
        
    def write2db(self):
        if self.db.db_write(self.coll_name, 
                            self.mongodb_item):
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