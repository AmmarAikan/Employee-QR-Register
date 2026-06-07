FROM python:3.11-slim

WORKDIR /app

# (اختياري) لو عندك requirements.txt سطرين تحت بيفيدوك
# COPY requirements.txt .
# RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "main1.py"]
