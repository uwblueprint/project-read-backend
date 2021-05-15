FROM python:3.9.2
ENV PYTHONUNBUFFERED=1
WORKDIR /code/
COPY requirements.txt /code/
RUN pip install -r requirements.txt
COPY . /code/
