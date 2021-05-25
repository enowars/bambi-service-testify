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
CMD ["python3", "testify.py"]