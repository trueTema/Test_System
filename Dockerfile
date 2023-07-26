FROM python:3.9

RUN pip install --upgrade pip && pip install telebot && pip install pysqlite3 && pip install debugpy

COPY . .


CMD ["python3", "./main.py"]