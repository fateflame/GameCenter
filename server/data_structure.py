# -*- coding:utf-8 -*-
'''
对一个连接，有 个状态，保存在User中
0表示未登录
1表示已登录
2表示在房间内
'''
import time
import json
import random
import socket

class Local:        # 记录本地database的数据
    def __init__(self, f):
        self.__data_location = f    # location of <account,password, livetime> file

        self.record_list = {}     # {account, [pwd, livetime, isOnline]} map for checking sign-in
        self.conection = {}  # {sock, User} map to record the state of each connection
        self.logged_users = {}      # {accout, User}
        self.room_list = {'hall': []}  # {roomname, [users]}，其中center表示未进入房间，在广场的用户
        self.room_question = {}     # {roomname, Question}，仅在答题期间非空，游戏结束后清空

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


class Question:
    def __init__(self):
        self.nums = [random.randint(1,10) for i in range(4)]
        self.nums.sort()
        self.winner = None
        self.max = None
        self.proposed_users = []        # 以第一次提交为准，记录下提交过结果的用户
        self.right_ans = None           # 记录当前获胜的答案


class User:         # 泛指已建立的各个连接，并非已登录的user
    def __init__(self, conn):
        self.conn = conn        # 连接后存在
        # 以下为登录后才记录的信息
        self.user_account = None        # 仅对已登录用户有效
        self.state = 0      # 0 for normal connection, not login
        self.login_time = None
        self.room = None        # 仅对已登录用户有效

    def sign_in(self, account, room):
        self.user_account = account
        self.login_time = time.time()
        self.state = 1      # 1 for already sign in
        self.room = room

    def log_out(self):
        self.state = 0
        self.user_account = None
        self.room = None
        livetime = time.time()-self.login_time
        self.login_time = None
        return livetime

    def close(self):
        if self.state != 0:
            self.log_out()

    def enter_room(self, roomname):
        self.state = 2
        self.room = roomname

    def exit_room(self, default_room):
        self.state = 1
        self.room = default_room


class Protocol:
    # 套接字包装类，重新recv和sendall函数以加上包头
    header_len = 4

    def __init__(self, conn):
        self.conn = conn

    def bind(self, address):
        return self.conn.bind(address)

    def connect(self, address):
        return self.conn.connect(address)

    def listen(self, backlog):
        return self.conn.listen(backlog)

    def accept(self):
        conn, addr = self.conn.accept()
        return Protocol(conn), addr

    def close(self):
        return self.conn.close()

    def recv(self, buf_size):
        try:
            header = self.conn.recv(self.header_len)
            if header == '':
                raise EOFError("Receive a eof from {}".format(self.getpeername()))
            elif header == '0000':
                return ''
            while len(header) < self.header_len:
                header += self.conn.recv(self.header_len-len(header))
            length = self.__parse_header(header)
            data = ""
            while length > buf_size:
                data += self.conn.recv(buf_size)
                length -= buf_size
            data += self.conn.recv(length)
            return data
        except ValueError:
            raise           # 可考虑强制关闭连接

    def __parse_header(self, header):
        try:
            header_length = int(header)
            if header_length < 0:
                raise ValueError('Unexpected negative length of data')
            return header_length
        except ValueError:
            raise             # 解析头部长度错误

    def sendall(self, msg):
        data_len = len(msg)

        if data_len > 9999:
            raise OverflowError("Cannot send a message more than 9999 words!")
        msg = '{:0>4}'.format(data_len) + msg
        self.conn.sendall(msg)

    def fileno(self):
        return self.conn.fileno()

    def getpeername(self):
        return self.conn.getpeername()