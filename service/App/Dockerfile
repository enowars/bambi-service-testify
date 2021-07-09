FROM python:3.8.7

WORKDIR App
COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt
RUN apt-get update && apt-get install -y dos2unix
COPY startup.sh .
RUN dos2unix startup.sh && apt-get --purge remove -y dos2unix
RUN chmod +x startup.sh
RUN ./startup.sh
COPY . .
EXPOSE 8000
ENV MYSQL_PWD=userpass
WORKDIR src

ENTRYPOINT [ "gunicorn", "-c", "gunicorn.conf.py", "testify:app" ]

ENV PYTHONUNBUFFERED=TRUE