FROM python:3

WORKDIR /app

COPY requirements.txt *.py .

RUN pip install --no-cache-dir -r requirements.txt

CMD [ "python", "main.py"]