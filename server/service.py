# -*- coding:utf-8 -*-
import data_structure
'''
针对服务器端本地存储的数据的写局限于此类中
'''


class Service:
    cmd_dict = {'$signin': 1,
                '$signup': 2,
                '$logout': 3}

    local_var = None

    def __init__(self, f):
        self.local_var = data_structure.Local(f)

    def service_program(self, user):
        data = user.conn.recv(1024)
        # 处理请求
        try:
            cmd = self.__parse_data(data)
        except ValueError as e:
            user.conn.sendall(e.message)
            return

        if user.state == 0:     # 未登录
            if cmd[0] > 2:
                user.conn.sendall("You must log in first")
                return
            elif cmd[0] == 1:
                msg = self.__login(cmd, user)
                user.conn.sendall(msg)
                return
            # TODO if cmd[0]==2

        elif user.state == 1:           # 已登录
            # TODO other functions
            if cmd[0] == 3:
                msg = self.__logout(user)
                user.conn.sendall(msg)
                return

    def __parse_data(self, string):
        # 将接受到的字符串处理成[cmd_no, args...]的形式，cmd_no表示指令编号
        cmd = string.split()
        if cmd.__len__() <= 0:
            raise ValueError("invalid command length")
        if not self.cmd_dict.has_key(cmd[0]) :        # 判断是否为合法命令
            raise ValueError("invalid command")
        cmd[0] = self.cmd_dict[cmd[0]]
        return cmd

    def __login(self, cmd, user):
        account = cmd[1]
        pwd = cmd[2]
        if user.state is 0:
            if self.local_var.record_list.has_key(account):  # 账号存在时验证密码
                if self.local_var.record_list[account][0] == pwd:
                    if not self.local_var.record_list[account][2]:   # not online yet
                        self.local_var.record_list[account][2] = True
                        user.sign_in(account)  # 修改登录状态
                        return "log in successful."
                    else:
                        return "this account is already logged in, please check"
            else:
                return "Wrong account or password"
        else:
            return "You have already logged in, try to log out first."


    def __logout(self, user):
        if user.state is 0:
            return "You haven't logged in yet."
        if user.state is 1:
            a = user.user_account
            t = user.log_out()
            self.local_var.record_list[a][1] += t
            self.local_var.record_list[a][2] = False
            return "logout successful"


