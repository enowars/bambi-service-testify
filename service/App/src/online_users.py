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
        sql = f.read()[27:-2]
        f.close()
        arr = tuple_string_to_list(sql)
        users = [i[1] for i in arr]
        return users
    except FileNotFoundError:
        return []
