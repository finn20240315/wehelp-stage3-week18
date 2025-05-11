from fastapi import FastAPI,Request,File,Form,UploadFile,HTTPException
# UploadFile: FastAPI 提供的檔案類型，支援大檔案上傳（stream 方式）
# HTTPException: 可以回傳 HTTP 錯誤（如 400、500）給前端
import boto3
# boto3: 操作 AWS S3 的套件
from botocore.exceptions import BotoCoreError,NoCredentialsError 
# BotoCoreError, NoCredentialsError: S3 操作時常見錯誤類型（如沒金鑰、網路錯等）
import os
# os: 讀取環境變數用
from dotenv import load_dotenv
import uuid
from pathlib import Path 
from fastapi.responses import JSONResponse,HTMLResponse
from fastapi.staticfiles import StaticFiles

from dotenv import load_dotenv
load_dotenv()

from pathlib import Path
from datetime import datetime

import db
db.init_table()  # 加這行就會自動初始化

from backend.model import db_connector
get_db_connection = db_connector.get_db_connection  # 之後繼續用原本寫法

# 👇 強制正確值
os.environ["S3_REGION"] = "ap-northeast-1"

# 👇 拿的是我們手動覆蓋後的值
S3_REGION = os.environ["S3_REGION"]
print("🧪 最終使用 region:", repr(S3_REGION))

app = FastAPI()

# ⬇️ 將 /frontend 對應到實際的 frontend 資料夾
app.mount("/frontend", StaticFiles(directory="frontend"), name="frontend")

# AWS 認證 ??
AWS_ACCESS_KEY_ID=os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY=os.getenv("AWS_SECRET_ACCESS_KEY")
S3_BUCKET_NAME=os.getenv("S3_BUCKET_NAME")
S3_REGION=os.getenv("S3_REGION")

# 建立一個 S3 客戶端，用來上傳檔案
# 這邊在幹嘛?

s3=boto3.client(
    "s3",
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    region_name=S3_REGION
)

@app.get("/", response_class=HTMLResponse)
async def root():
    index_file = Path("frontend/html/index.html")
    return index_file.read_text(encoding="utf-8")

@app.post("/api/messages")
async def post_messages(request:Request): #??
    data=await request.json() 
    print("🧪 ",data)
    content=data.get("content")
    img_url=data.get("img_url")

    if not content or not img_url:
        print("❌ 錯誤：欄位填寫不完全")
        return JSONResponse(content={"error":"欄位填寫不完全"},status_code=400)
        # 400-499: Client Error


    conn=get_db_connection()
    cursor=conn.cursor(dictionary=True)
    # execute() 是 cursor 的方法，不是 conn 的方法
    cursor.execute("""
    INSERT INTO messages (content,img_url) VALUES (%s,%s)
                 """, (content, img_url)) # NOW() 是 MySQL 的語法，會自動填入當下時間 = DEFAULT CURRENT_TIMESTAMP
    conn.commit()
    cursor.close()
    conn.close()
    
    return JSONResponse({"ok":True,"message":"留言建立成功"})

@app.get("/api/messages")
async def get_messages():
    conn=get_db_connection()
    cursor=conn.cursor(dictionary=True)
    cursor.execute("""
    SELECT * FROM messages ORDER BY created_at DESC
    """)
    results=cursor.fetchall()
    cursor.close()
    conn.close()

    # ✅ 轉換 created_at 為字串，避免 JSON 序列化錯誤
    for r in results:
        if isinstance(r["created_at"], datetime):
            r["created_at"] = r["created_at"].strftime("%Y-%m-%d %H:%M:%S")

    return JSONResponse({
        "success": True,
        "message": "撈取留言成功",
        "data": results
    })
# https://bucket-name.s3.region.amazonaws.com/檔名
# https://{S3_BUCKET_NAME}.s3.{S3_REGION}.amazonaws.com/{new_filename}


@app.post("/api/upload")
async def post_upload(file:UploadFile=File(...)):
    try: # 哪裡有說到他會接收前端用 multipart/form-data 傳來的圖片?
        file_extension=file.filename.split(".")[-1]
        # 用.區隔字串,[-1]是什麼?
        new_filename=f"{uuid.uuid4()}.{file_extension}"
        # 為什麼要定義 filename?
        s3.upload_fileobj(
            file.file, # 是物件?
            S3_BUCKET_NAME, # 傳到這裡?我要直接寫出來嗎?
            new_filename,
            ExtraArgs={"ContentType":file.content_type} # 什麼類型?
        )
        img_url=f"https://{S3_BUCKET_NAME}.s3.{S3_REGION}.amazonaws.com/{new_filename}"
        return {"ok":True,"url":img_url}

    except (BotoCoreError,NoCredentialsError) as e:
        raise HTTPException (status_code=500,detail=str(e))    
    except Exception as e:
        print("❌ 上傳失敗", e)
        raise HTTPException(status_code=500, detail="圖片上傳失敗")


# # 前端送圖片（form-data）
#         ↓
# # FastAPI 用 UploadFile 取得圖片
#         ↓
# # 呼叫 boto3 上傳圖片至 S3
#         ↓
# # 組網址回傳給前端（可用於 img src）


# # [前端瀏覽器]
#     |
#     |-- (1) 選圖片 → 送出 form（multipart/form-data）
#     |
#     v
# [FastAPI Server]
#     |
#     |-- (2) 用 UploadFile 取得檔案
#     |-- (3) 用 boto3.upload_fileobj() 上傳圖片至 S3
#     |
#     v
# [AWS S3 Bucket]
#     |
#     |-- (4) 儲存圖片，產生公開網址
#     |
#     v
# [FastAPI Server]
#     |
#     |-- (5) 組網址 → 回傳 JSON 給前端
#     |
#     v
# [前端瀏覽器]
#     |
#     |-- (6) 顯示圖片：<img src="S3網址">


# 1. 前端用 `<form>` 上傳圖片（`multipart/form-data`）
# 2. 後端 FastAPI 接收圖片（`UploadFile`）
# 3. 使用 `boto3` 把圖片上傳至 S3
# 4. 回傳 S3 圖片 URL（給前端使用）  