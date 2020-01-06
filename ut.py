import pymysql
from sqlalchemy import create_engine
import pandas as pd

dbhost = "jnc-zabbix.cotpwdfxy0tl.rds.cn-northwest-1.amazonaws.com.cn"
dbport = 3306
dbuser = "jnczabbix"
dbpasswd = "W2df6s9&GA^iVKCI"
dbdb = "zabbix"

db = pymysql.connect(host=dbhost,
                   port=dbport,
                   user=dbuser,
                   passwd=dbpasswd,
                   db=dbdb)

sqlalchemyconn = create_engine('mysql+pymysql://%s:%s@%s:%s/%s' % (dbuser, dbpasswd, dbhost, dbport, dbdb),pool_size=20, max_overflow=0)
sql = '''select * from trends
            where itemid=34978'''
result = pd.read_sql(sql, db)
print(result)
