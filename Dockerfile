FROM python:3.9

WORKDIR /app

COPY requirements.txt /app

RUN pip install -r requirements.txt

ENV DB_HOST host.docker.internal

COPY . /app

CMD ["python", "main.py"]
