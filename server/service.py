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

        if user.state == 0:
            if cmd[0] > 2:
                user.conn.sendall("You must log in first")
                return
            if cmd[0] == 1:
                msg = self.login(cmd, user)
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

    def login(self, cmd, user):
        if user.state is 0:
            if self.__check_login(cmd[1], cmd[2]):
                user.sign_in()                   # 修改登录状态
                return "log in successful."
            else:
                return "wrong password or account."
        else:
            return "You have already logged in, try to log out first."










    def __logout(self):
        if self.stat is 0:
            return "You haven't logged in yet."
        if self.stat is 1:
            # 停止记录时间并保存到本地
            self.stat = 0           # 修改登录状态
            return "logout successful"

    @staticmethod
    def __check_login(account, pwd):
        if account in Service.__user_list:  # 账号存在时验证密码
            return Service.__user_list[account].password == pwd
        return False
