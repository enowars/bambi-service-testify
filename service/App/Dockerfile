FROM python:3.8.7

COPY . /App

WORKDIR /App
RUN pip3 install -r src/requirements.txt

EXPOSE 8000
ENV MYSQL_PWD=userpass
ENV PYTHONUNBUFFERED=TRUE

WORKDIR src
ENTRYPOINT [ "gunicorn", "-c", "gunicorn.conf.py", "testify:app" ]
