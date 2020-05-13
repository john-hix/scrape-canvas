FROM python:3

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN mkdir data
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENTRYPOINT ["python3", "./canvas-scraper.py"]
