FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY reader.py update_reading_age.py ./

CMD ["python", "reader.py"]
