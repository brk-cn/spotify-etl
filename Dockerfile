FROM python:3.9-slim

WORKDIR /spotify-etl

COPY . /spotify-etl

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8888

CMD ["python", "app.py"]
