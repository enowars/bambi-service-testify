import subprocess


def get_online_users():
    subprocess.Popen(
        'mysqldump -h testify-mysql -u usertable_user user_database --no-tablespaces --lock-tables=false '
        '--no-create-info --net-buffer-length=1048576 --extended-insert=FALSE --compact --hex-blob --where="1 and '
        'username not like \'doctor%\' order by user_id DESC limit 1000" > user_data/online_users/dump.sql',
        shell=True).wait()
    try:
        f = open("user_data/online_users/dump.sql", "r")
        sql = f.readlines()
        f.close()
        users = [i.split(',')[1] for i in sql]
        return users
    except FileNotFoundError:
        return []
