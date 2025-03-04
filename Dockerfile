FROM python:latest

WORKDIR /app

COPY main.py ./main.py
RUN pip install --upgrade pip && pip install tinydb

CMD ["python", "main.py"]
