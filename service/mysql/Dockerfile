FROM mysql

ENV MYSQL_DATABASE user_database

COPY sql-scripts/ /docker-entrypoint-initdb.d/

ENV MYSQL_ROOT_PASSWORD=root

ENV MYSQL_USER=usertable_user

ENV MYSQL_PASSWORD=userpass