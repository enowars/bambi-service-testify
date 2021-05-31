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
    return []
