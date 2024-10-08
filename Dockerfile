FROM python:latest
WORKDIR /app/
COPY . /app/
RUN pip install -r ./requirements.txt
CMD uvicorn --host=0.0.0.0 --port 8083 main:app
