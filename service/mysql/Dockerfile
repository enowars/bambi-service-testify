FROM mysql

ENV MYSQL_DATABASE company

COPY ./sql-scripts/ /docker-entrypoint-initdb.d/

ENV MYSQL_ROOT_PASSWORD=root