FROM python:3.8.7

WORKDIR App
COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt
COPY . .
EXPOSE 8000
ENV MYSQL_PWD=userpass
RUN chmod +x run.sh
RUN ./run.sh
WORKDIR src
CMD ["python3", "testify.py"]