# -*- coding:utf-8 -*-
'''
对一个连接，有 个状态，保存在User中
0表示未登录
1表示已登录
2表示在房间内
'''
import time
import json


class Local:        # 记录本地database的数据
    def __init__(self, f):
        self.__data_location = f    # location of <account,password, livetime> file

        self.record_list = {}     # {account, [pwd, livetime, isOnline]} map for checking sign-in
        self.conection = {}  # {sock, User} map to record the state of each connection
        self.logged_users = {'center': []}  # {roomname, [users]}，其中center表示未进入房间，在广场的用户

        self.__read_data()

    def __read_data(self):
        try:
            f = open(self.__data_location, 'r')
            self.record_list = json.load(f)
            f.close()
        except IOError:
            print ("cannot find the file, exit")
            exit(1)
        except:
            print("incorrect data in database, please check")
            raise


class User:         # 泛指已建立的各个连接，并非已登录的user
    def __init__(self, conn):
        self.user_account = None        # 仅对已登录用户有效
        self.state = 0      # 0 for normal connection, not login
        self.signin_time = None
        self.room = 'center'
        self.conn = conn

    def sign_in(self, account):
        self.user_account = account
        self.signin_time = time.time()
        self.state = 1      # 1 for already sign in

    def log_out(self):
        self.state = 0
        self.user_account = None
        live_time = time.time()-self.signin_time
        self.signin_time = None
        return live_time

    def close(self):
        if self.state != 0:
            self.log_out()

