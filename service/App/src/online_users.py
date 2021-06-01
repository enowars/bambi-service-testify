def tuple_string_to_list(test_str):
    res = []
    temp = []
    for token in test_str.split(","):
        num = str(token.replace("(", "").replace(")", ""))
        temp.append(num)
        if ")" in token:
            res.append(tuple(temp))
            temp = []
    return res


def get_online_users():
    try:
        f = open("user_data/online_users/dump.sql", "r")
        sql = f.readlines()
        f.close()
        users = [i.split(',')[1] for i in sql]
        return users[-50:]
    except FileNotFoundError:
        return []
