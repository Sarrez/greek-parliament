FROM python:3.10.1-buster
RUN mkdir /app
WORKDIR /app

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

COPY . /app
RUN pip install -r requirements.txt

CMD python python3 hello.py create_db.py