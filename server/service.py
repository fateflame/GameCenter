# -*- coding:utf-8 -*-
'''
针对服务器端本地存储的数据的写局限于此类中

可用命令：
signin/login 登录
signup 注册
signout/logout 登出
'''
import data_structure


class Service:
    # 未登录命令范围0-10，大厅专用命令范围11-20， 房间内专用命令21-30，登录后通用命令31+
    cmd_dict = {
                '$signin': 1,
                '$signup': 2,

                '$creatroom':11,
                '$enter':12,
                '$lsroom' :13,

                '$exitroom': 21,

                '$logout': 31,
                '$chatall':32,
                '$chat':   33,
                '$chatto': 34,
                '$getroom':35,
                }

    local_var = None

    def __init__(self, f):
        self.file_location = f
        self.local_var = data_structure.Local(self.file_location)
        self.default_room = self.local_var.room_list.keys()[0]      # 初始化时只有一个房间

    def welcome_program(self, conn):
        print ('Connected by', conn.getpeername())
        info = "Welcome!\nYou could log in, or sign up a new account"
        conn.sendall(info)

    def service_program(self, conn, data):
        user = self.local_var.conection[conn]
        # 处理请求
        try:
            cmd = self.__parse_data(data)
        except ValueError as e:
            conn.sendall(e.message)
            return

        if user.state == 0:     # 未登录
            if cmd[0] > 10:
                conn.sendall("You must log in first")
                return
            elif cmd[0] == 1:
                msg = self.__login(cmd, user)
                conn.sendall(msg)
                return
            elif cmd[0] == 2:
                msg = self.__signup(cmd)
                conn.sendall(msg)

        elif user.state >= 1:   # 已登录
            if cmd[0] == 31:
                msg = self.__logout(user)
                return conn.sendall(msg)
            elif cmd[0] == 32:
                return self.__chatall(conn, cmd)
            elif cmd[0] == 33:
                return self.__chat_in_room(conn, cmd)
            elif cmd[0] == 34:
                return self.__chat_to(conn, cmd)
            elif cmd[0] == 35:
                return self.__get_room(conn)

            elif user.state == 1:     # 在大厅
                if cmd[0] <= 10:
                    return conn.sendall("You mush log out first.")
                elif 20 < cmd[0] <= 30:
                    return conn.sendall("You are in the {}, try to enter a room first.".format(self.default_room))
                elif cmd[0] == 11:
                    self.create_room(conn, cmd)
                elif cmd[0] == 12:
                    self.enter_room(conn, cmd)
                elif cmd[0] == 13:
                    self.__list_room(conn)
            elif user.state == 2:   # 在房间
                if cmd[0] <= 10:
                    return conn.sendall("You mush log out first.")
                elif cmd[0] <= 20:
                    return conn.sendall("You are in a room ,try to exit room first.")
                elif cmd[0] == 21:
                    self.exit_room(conn)


    def close_conn(self, conn):
        u = self.local_var.conection[conn]
        if u.state != 0:
            self.__logout(u)
        self.local_var.conection.pop(conn)
        conn.close()

    def __parse_data(self, string):
        # 将接受到的字符串处理成[cmd_no, args...]的形式，cmd_no表示指令编号
        cmd = string.split()
        if cmd.__len__() <= 0:
            raise ValueError("invalid command length")
        if not self.cmd_dict.has_key(cmd[0]):        # 判断是否为合法命令
            raise ValueError("invalid command")
        cmd[0] = self.cmd_dict[cmd[0]]
        return cmd

    def __login(self, cmd, user):
        if len(cmd) < 3:
            return "Wrong arguments numbers"
        account = cmd[1]
        pwd = cmd[2]
        if user.state is 0:
            if self.local_var.record_list.has_key(account):  # 账号存在时验证密码
                if self.local_var.record_list[account][0] == pwd:
                    if not self.local_var.record_list[account][2]:   # not online yet
                        self.local_var.record_list[account][2] = True
                        user.sign_in(account, self.default_room)  # 修改登录状态
                        self.local_var.logged_users[account] = user
                        self.local_var.room_list[self.default_room].append(user)  # 进入大厅
                        return "log in successful."
                    else:
                        return "this account is already logged in, please check"
            return "Wrong account or password"
        else:
            return "You have already logged in, try to log out first."

    def __logout(self, user):
        if user.state is 0:
            return "You haven't logged in yet."
        if user.state is 2:
            self.__exit_room(user)
        self.local_var.room_list[user.room].remove(user)    # 从大厅移除

        a = user.user_account
        t = user.log_out()
        self.local_var.record_list[a][1] += t
        self.local_var.record_list[a][2] = False
        self.local_var.logged_users.pop(a)
        return "logout successful"

    def __signup(self, cmd):
        if len(cmd) < 3:
            return "Wrong arguments numbers"
        a = cmd[1]
        p = cmd[2]
        if self.local_var.record_list.has_key(a):
            return "The account already exists"
        else:
            self.local_var.record_list[a] = [p, 0, False]
            return "Signup successfully. You can sign in with it now"

    def __chatall(self, sender_conn, cmd):
        # 向除自己外的所有用户发送消息
        if len(cmd) < 2:
            sender_conn.sendall("Wrong arguments number. You need to input massage")
            return
        cmd.pop(0)
        sender = self.local_var.conection[sender_conn].user_account
        msg = sender + "(public):" + " ".join(cmd)
        for user in self.local_var.logged_users.values():
            if user.conn != sender_conn:
                user.conn.sendall(msg)
        return

    def __chat_in_room(self, sender_conn, cmd):
        if len(cmd) < 2:
            sender_conn.sendall("Wrong arguments number. You need to input massage")
            return
        cmd.pop(0)
        sender = self.local_var.conection[sender_conn].user_account
        msg = sender + "(room):" + " ".join(cmd)
        room = self.local_var.conection[sender_conn].room
        for user in self.local_var.room_list[room]:
            if user.conn != sender_conn:
                user.conn.sendall(msg)

    def __chat_to(self, sender_conn, cmd):
        if len(cmd) < 3:
            return sender_conn.sendall("Wrong arguments number. You need to input massage")
        receiver = cmd[1]
        sender = self.local_var.conection[sender_conn].user_account

        if receiver == sender:
            return sender_conn.sendall("You cannot send a message to yourself")
        if receiver not in self.local_var.logged_users.keys():
            return sender_conn.sendall("No such user or the user is not online")

        del cmd[0:2]        # 删除前两个元素
        msg = sender + "(private):" + " ".join(cmd)
        self.local_var.logged_users[receiver].conn.sendall(msg)

    def __get_room(self, conn):
        # 回显用户当前所在房间
        msg = "You are in '{}'".format(self.local_var.conection[conn].room)
        conn.sendall(msg)

    def __list_room(self, conn):
        rooms = self.local_var.room_list.keys()
        rooms.remove(self.default_room) # 除去大厅外
        conn.sendall(rooms.__str__())

    def create_room(self, sender_conn, cmd):
        # precondition: 用户已登录，且在大厅中
        user = self.local_var.conection[sender_conn]
        if user.state != 1:
            raise ValueError("user is not in the room")
        if len(cmd) < 2:
            return sender_conn.sendall("Wrong arguments number. You need to input massage")
        cmd.pop(0)
        roomname = " ".join(cmd)
        if self.local_var.room_list.has_key(roomname):
            return sender_conn.sendall("The name is already in use, please change a room name")

        self.local_var.room_list[roomname] = []
        self.__enter_room(user, roomname)
        sender_conn.sendall("Create room successfully. You are in the room '{}'.".format(roomname))

    def enter_room(self, sender_conn, cmd):
        # precondition: 用户已登录，且在大厅中
        user = self.local_var.conection[sender_conn]
        if user.state != 1:
            raise ValueError("user is not in the room")
        if len(cmd) < 2:
            return sender_conn.sendall("Wrong arguments number. You need to input massage")
        cmd.pop(0)
        roomname = " ".join(cmd)
        if roomname == user.room:
            return sender_conn.sendall("You are already in the room")
        if not self.local_var.room_list.has_key(roomname):
            return sender_conn.sendall("No such room, please check")
        self.__enter_room(user, roomname)
        sender_conn.sendall("Enter the room {} successfully.".format(roomname))

    def __enter_room(self, user, roomname):
        # precondition: roomname是有效房间名
        self.local_var.room_list[user.room].remove(user)    # 从原房间（大厅）移除
        self.local_var.room_list[roomname].append(user)
        user.enter_room(roomname)

    def exit_room(self, sender_conn):
        # precondition: 发送用户已在一个房间内
        user = self.local_var.conection[sender_conn]
        if user.state != 2:
            raise ValueError("User is not in the room")
        self.__exit_room(user)
        sender_conn.sendall("Exit successfully")

    def __exit_room(self, user):
        room = user.room
        user.exit_room(self.default_room)
        self.local_var.room_list[room].remove(user)
        self.local_var.room_list[self.default_room].append(user)    # 回到大厅
        if len(self.local_var.room_list[room]) == 0 and room != self.default_room:
            self.local_var.room_list.pop(room)  # 房间没人则关闭房间