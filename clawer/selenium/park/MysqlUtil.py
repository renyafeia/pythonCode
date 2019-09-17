import pandas as pd
from sqlalchemy import create_engine


class MysqlUtil:
    def __init__(self, host, port, username, password, db, table):
        self.host = host
        self.port = port
        self.username = username
        self.db = db
        self.table = table
        self.write_mode = 'append'
        self.connect_url = 'mysql+pymysql://' + username + ':' + password + '@' + host + ':' + port + '/' + db + '?charset=utf8'
        self.mysql_connect = create_engine(self.connect_url)

    def df_write_mysql(self, data):
        pd.io.sql.to_sql(data, self.table, self.mysql_connect, schema=self.db, if_exists=self.write_mode)
        print('write  to mysql finish')


if __name__ == '__main__':

    # 初始化数据库连接，使用pymysql模块
    engine = create_engine('mysql+pymysql://root:123456@localhost:3306/mytest')
    #df = pd.DataFrame({'id': [1, 2, 3], 'name': ['zhangsan', 'lisi', 'wangermazi']})
    df = pd.DataFrame({'name': ['zhangsan', 'lisi', 'wangermazi']})
    df.to_sql('table1', engine,if_exists='append',index=False)
    print('ssss')
