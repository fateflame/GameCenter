# -*- coding:utf-8 -*-
import socket
import select
import data_structure
import ConfigParser
import json
import service
import threading
import thread
import time
import os
import datetime


class Server:

    def __init__(self, f='./config'):
        # 读取配置文件
        self.config = f
        cf = ConfigParser.ConfigParser()
        cf.read(self.config)

        self.__port = cf.getint('server', 'port')
        self.__host = cf.get('server', 'host')
        self.__backlog = cf.getint('server', 'backlog')
        self.__database_location = cf.get('server', 'database_location')
        self.pipe_file = cf.get('server', 'pipe_file')
        # 服务器连接管理变量
        self.service = service.Service(self.__database_location)

        self.ser_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.ser_sock.bind((self.__host, self.__port))

        self._build_local_sock()

        self.run()
        self.__close()

    def _build_local_sock(self):
        # 建立一对连接用以子线程与主线程之间通信
        local_sock_ser = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self.local_sock_sub = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        if os.path.exists(self.pipe_file):
            os.unlink(self.pipe_file)
        local_sock_ser.bind(self.pipe_file)
        local_sock_ser.listen(1)
        self.local_sock_sub.connect(self.pipe_file)
        self.local_sock_main, addr = local_sock_ser.accept()
        local_sock_ser.close()  # 关闭监听套接字

    def run(self):
        t = threading.Thread(target=self.server_ctrl, args=[])
        # 启动一个线程控制服务器，遇到exit，则中断主线程
        t.start()
        self.listen()
        t.join()

    def listen(self):
        self.ser_sock.listen(self.__backlog)

        while True:
            rset = [self.ser_sock, self.local_sock_main] + self.service.local_var.conection.keys()
            wset = []
            xset = []

            r, w, x = select.select(rset, wset, xset, None)
            nready = len(r+w+x)

            if self.local_sock_main in r:
                data = self.local_sock_main.recv(1024)
                if data == "exit":
                    break
                elif data == 'game':
                    # TODO: 给各个房间发送题目
                    self.service.send_question()
                elif data == 'gameover':
                    # TODO 发布游戏结果
                    self.service.pub_result()

            elif self.ser_sock in r:      # 监听套接字，新的连接
                conn, cli_addr = self.ser_sock.accept()
                self.service.local_var.conection[conn] = data_structure.User(conn)
                self.service.welcome_program(conn)
                nready -= 1
                if nready <= 0:
                    continue
            for conn in r:              # 已连接套接字
                if self.service.local_var.conection.has_key(conn):
                    data = conn.recv(1024)
                    if len(data) == 0:
                        print "close a client"
                        # TODO 退出用户，从各列表中删除对应连接还用户，关闭连接
                        self.service.close_conn(conn)        # remove close connection
                    elif len(data) > 0:
                        # TODO provide service here
                        self.service.service_program(conn, data)
                    nready -= 1
                    if nready <= 0:
                        break

    def __close(self):
        self.local_sock_sub.close()
        self.local_sock_main.close()
        for conn, user in self.service.local_var.conection.iteritems():
            if user.user_account:
                conn.sendall("close server")
                # 主动退出所有账号，并记录数据
                account = user.user_account
                self.service.local_var.record_list[account][1] += user.log_out()
                self.service.local_var.record_list[account][2] = False
            # 关闭所有连接
            conn.close()
        self.ser_sock.close()       # 关闭监听套接字
        try:
            f = open(self.__database_location, 'w')
            json.dump(obj=self.service.local_var.record_list, fp=f)
            f.close()
        except:
            raise
        exit(0)

    def server_ctrl(self):
        while True:
            cmd = raw_input("press cmd to control server\n")
            if cmd == 'exit':
                c = raw_input('Are you sure to exit server program?\nPress "y" to continue, else to return\n')
                if c == 'y':
                    return self.local_sock_sub.sendall("exit")
            elif cmd == "game":
                self._game21()
            else:
                print("Invalid cmd, return")

    def game21(self):       # 调整第一次game的时间
        self._game21()
        interval = 3600
        threading.Timer(interval, self.game21, ())           # 准备下次

    def _game21(self):
        self.local_sock_sub.sendall("game")
        time.sleep(90)
        self.local_sock_sub.sendall("gameover")


def approach_half_hour():
    t0 = datetime.datetime.now()
    t1 = datetime.datetime(t0.year, t0.month, t0.day, t0.hour, 30, 0)
    if t1 < t0:
        t1 = datetime.datetime(t0.year, t0.month, t0.day, t0.hour + 1, 30, 0)
    while True:
        delta = (t1 - t0)
        if delta.total_seconds() > 10:
            time.sleep(3/4*delta)       # 渐进
        else:
            time.sleep(delta)
            return
        t0 = datetime.datetime.now()


if __name__ == "__main__":
    s = Server()