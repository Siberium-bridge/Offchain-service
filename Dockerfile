FROM python:3.10

ENV PYTHONPATH=/app
COPY requirements.txt .
RUN python -m pip install -r requirements.txt

WORKDIR /app

COPY src/ .
CMD python3 main.py