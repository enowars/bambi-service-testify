FROM python:3.8.7

WORKDIR App
COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["python3", "src/testify.py"]