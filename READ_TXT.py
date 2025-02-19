def read_users(file_path):
    users = []
    with open(file_path, "r") as f:
        blocks = f.read().split("===")  # 分割区块
        for block in blocks:
            user = {}
            lines = block.strip().split("\n")
            for line in lines:
                if ": " in line:
                    key, value = line.split(": ", 1)
                    user[key] = value
            if user:  # 避免空区块
                users.append(user)
    return users

# 示例调用
users = read_users("users.txt")
print(users[0]["Username"])  # 输出 "alice_customer"