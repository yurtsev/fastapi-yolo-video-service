FROM python:3.10-slim

WORKDIR /backend

COPY ./requirements.txt /backend/requirements.txt
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

COPY ./src /backend/src

CMD uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload