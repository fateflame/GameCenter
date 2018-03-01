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
    cmd_dict = {
                '$signin': 1,
                '$signup': 2,
                '$logout': 3,
                '$chatall': 4,
                '$chat':    5,
                '$chatto':  6,

                }

    local_var = None

    def __init__(self, f):
        self.file_location = f
        self.local_var = data_structure.Local(self.file_location)

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
            if cmd[0] > 2:
                conn.sendall("You must log in first")
                return
            elif cmd[0] == 1:
                msg = self.__login(cmd, user)
                conn.sendall(msg)
                return
            elif cmd[0] == 2:
                msg = self.__signup(cmd)
                conn.sendall(msg)

        elif user.state == 1:           # 已登录
            # TODO other functions
            if cmd[0] == 3:
                msg = self.__logout(user)
                conn.sendall(msg)
                return
            elif cmd[0] == 4:
                self.__chatall(conn, cmd)
            '''
            elif cmd[0] == 5:
                # TODO 向房间内除自己外的所有用户发送消息
                self.__chat_in_room(conn, cmd)
            elif cmd[0] == 6:
                # TODO 向非自己的一个用户发送消息
                self.__chat_to(conn, cmd)
            '''

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
                        user.sign_in(account)  # 修改登录状态
                        self.local_var.logged_users['center'].append(user)  # 进入大厅
                        return "log in successful."
                    else:
                        return "this account is already logged in, please check"
            return "Wrong account or password"
        else:
            return "You have already logged in, try to log out first."

    def __logout(self, user):
        if user.state is 0:
            return "You haven't logged in yet."
        else:
            self.local_var.logged_users[user.room].remove(user)     # 退出房间
            a = user.user_account
            t = user.log_out()
            self.local_var.record_list[a][1] += t
            self.local_var.record_list[a][2] = False
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

    def __chatall(self, conn, cmd):
        # 向除自己外的所有用户发送消息
        if len(cmd) < 2:
            conn.sendall("Wrong arguments number. You need to input massage")
        cmd.remove(cmd[0])
        msg = self.local_var.conection[conn].user_account + ":" + " ".join(cmd)
        for user_list in self.local_var.logged_users.values():
            for u in user_list:
                if u.conn != conn:
                    u.conn.sendall(msg)
        return