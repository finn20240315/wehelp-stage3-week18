# 使用官方 Python 映像檔
FROM python:3.11-slim 
# 設定工作目錄
WORKDIR /app
# 複製所有檔案到容器內 (= COPY . . # 複製當前資料夾所有檔案到容器中)
COPY . /app
# 安裝相依套件
RUN pip install --upgrade pip && pip install -r requirements.txt
# 開放 port 8000 給外部連線
EXPOSE 8000
# 啟動 FastAPI
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
