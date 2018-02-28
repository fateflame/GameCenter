# -*- coding:utf-8 -*-
'''
对一个连接，有 个状态，保存在User中
0表示未登录
1表示已登录
'''
import time


class Local:        # 记录本地database的数据
    def __init__(self, f="./database"):
        self.__data_location = f    # location of <account,password> file
        self.record_list = {}     # <account, record> map for checking sign-in

        self.__read_data()

    def __read_data(self):
        try:
            f = open(self.__data_location, 'r')
            user_data = f.readlines()
            # 将读入的每一行用户数据转换为dict的一条记录
            for user in user_data:
                try:
                    temp = Record(user)
                    self.record_list[temp.account] = temp
                except IndexError:
                    print ("invalid user data")
            f.close()
        except IOError:
            print ("please check if the database location is correct!")
            exit(1)
        except ValueError:
            print ("cannot find the file, exit")
            exit(1)


class User:
    def __init__(self, conn, addr):
        self.conn = conn
        self.address = addr
        self.state = 0      # 0 for normal connection, not login
        self.signin_time = None

    def sign_in(self):
        self.signin_time = time.time()
        self.state = 1      # 1 for already sign in

    def log_out(self):
        self.state = 0
        live_time = time.time()-self.signin_time
        return live_time

    def close(self):
        if self.state != 0:
            self.log_out()



class Record:
    def __init__(self, str):
        data = str.split()
        if data.__len__() != 3:
            raise IndexError('incompatible element numbers')
        self.account = data[0]
        self.password = data[1]
        self.time = data[2]