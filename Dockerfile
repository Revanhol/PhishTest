FROM python:3.12.3-slim

WORKDIR /PhishTest

COPY requirements.txt requirements.txt

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV PYTHONUNBUFFERED 1

CMD ["python", "phishtest/manage.py", "runserver", "0.0.0.0:8000"]