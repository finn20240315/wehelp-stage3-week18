# import backend.model.db_connector as get_db_connector
# 這是匯入整個模組，並幫它取名叫 get_db_connector
from backend.model.db_connector import get_db_connection
# 這是直接匯入模組中的 get_db_connection() 函式
import os

def init_table():
    conn = None
    cursor = None
    
    try:
        conn=get_db_connection()
        cursor=conn.cursor(dictionary=True)#??
        cursor.execute("""
    CREATE TABLE IF NOT EXISTS messages(
            id INT PRIMARY KEY AUTO_INCREMENT,
            content TEXT,
            img_url TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL)
        """)
        print("資料表 messages 建立完畢")
        print("✅ 正在連線到資料庫：", os.getenv("MYSQL_HOST"))

    except Exception as e:
        print("資料表 messages 建立失敗", e)
    finally:
        if cursor:
            cursor.close()#??
        if conn:
            conn.close()#??

# ⬇️ 關鍵：只有直接執行這個檔案時才會跑
if __name__ == "__main__":
    init_table()