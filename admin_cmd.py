import api

user_system = api.UserSystem()

print("admin portal")
while 1:
    cmd = input(">> ")
    if cmd == "usage":
        print("add user: add {username} {pwd}")
        print("remove user: rm {username}")
        print("check user: check {username} {pwd}")
        print("get all user: ls")

    elif cmd[:3] == "add":
        user_name = cmd.split(" ")[1]
        user_pwd = cmd.split(" ")[2]
        user_system.add_user(user_name=user_name, user_pwd=user_pwd)

    elif cmd[:2] == "rm":
        user_name = cmd.split(" ")[1]
        user_system.remove_user(user_name=user_name)

    elif cmd[:2] == "ls":
        raw = user_system.get_all_users()
        for item in raw.items():
            print(item[0], ": ", item[1])

    elif cmd[:5] == "check":
        user_name = cmd.split(" ")[1]
        user_pwd = cmd.split(" ")[2]
        if user_system.check_user(user_name=user_name, user_pwd=user_pwd):
            print("valid")
        else:
            print("fail")
