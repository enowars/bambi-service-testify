FROM python:3.8.7

WORKDIR App
COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt
COPY startup.sh .
RUN chmod +x startup.sh
RUN ./startup.sh
COPY . .
EXPOSE 8000
ENV MYSQL_PWD=userpass
WORKDIR src

ENTRYPOINT [ "gunicorn", "-c", "gunicorn.conf.py", "testify:app" ]

ENV PYTHONUNBUFFERED=TRUE