import os
from dotenv import load_dotenv
from mysql.connector import pooling,Error

load_dotenv()

try:
    mysql_pool=pooling.MySQLConnectionPool(
        pool_name="mypool",
        pool_size=32,
        pool_reset_session=True, # 每次從連線池中取出連線時會自動重設資料庫狀態
        host=os.getenv("MYSQL_HOST"),
        user=os.getenv("MYSQL_USER"),
        password=os.getenv("MYSQL_PASSWORD"),
        database=os.getenv("MYSQL_DATABASE"),
        charset="utf8mb4"
    )
    print("📡 正在連線到資料庫主機：", os.getenv("MYSQL_HOST"))

except Error as e:
    print("連線池建立失敗",e)
    mysql_pool=None #??
    # 是保險措施：萬一連線池建立失敗，程式繼續跑時就不會報錯未定義，
    # 而是之後使用 mysql_pool 時你可以檢查是否為 None 再做處理。
    
def get_db_connection():#??
    if mysql_pool is None: #??
        raise RuntimeError("MySQL 連線池尚未初始化")#??
    return mysql_pool.get_connection()#??