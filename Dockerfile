# Dùng Python 3.9 slim (nhẹ, nhanh)
FROM python:3.11-slim

WORKDIR /app

# Không cần cài gcc, cmake, zlib nữa!

COPY requirements.txt .

# Cài đặt thư viện (nhanh như gió)
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8501

CMD ["streamlit", "run", "app.py", "--server.address=0.0.0.0"]