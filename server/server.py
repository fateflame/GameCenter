# -*- coding:utf-8 -*-
import socket
import select
import data_structure
import ConfigParser
import json
import service
import threading
import thread


class Value:            # 服务器状态数据
    def __init__(self):
        self.conection = {}  # <sock, User> map to record the state of each connection


class Server:

    def __init__(self, f='./config'):
        # 退出标志
        self.__exit_flag = False
        # 读取配置文件
        self.config = f
        cf = ConfigParser.ConfigParser()
        cf.read(self.config)

        self.__port = cf.getint('server', 'port')
        self.__host = cf.get('server', 'host')
        self.__backlog = cf.getint('server', 'backlog')
        self.__database_location = cf.get('server', 'database_location')
        # 服务器连接管理变量
        self.var = Value()
        self.service = service.Service(self.__database_location)

        self.ser_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.ser_sock.bind((self.__host, self.__port))

        self.run()

    def run(self):
        t = threading.Thread(target=self.listen, args=[])
        # 启动一个线程控制服务器
        t.start()
        self.server_ctrl()
        t.join()# TODO 阻塞于select时无法顺利退出，待修改
        self.__close()

    def listen(self):
        self.ser_sock.listen(self.__backlog)

        while not self.__exit_flag:
            rset = [self.ser_sock] + self.var.conection.keys()
            wset = []
            xset = []

            r, w, x = select.select(rset, wset, xset, None)
            nready = len(r+w+x)

            if self.ser_sock in r:      # 监听套接字，新的连接
                conn, cli_addr = self.ser_sock.accept()
                self.var.conection[conn] = data_structure.User(conn)
                self.welcome_program(conn)
                nready -= 1
                if nready <= 0:
                    continue
            for conn in r:              # 已连接套接字
                if self.var.conection.has_key(conn):
                    data = conn.recv(1024)
                    if len(data) == 0:
                        print "close a client"
                        conn.close()
                        self.var.conection.pop(conn)        # remove close connection
                    elif len(data) > 0:
                        # TODO provide service here
                        u = self.var.conection[conn]
                        self.service.service_program(u, data)
                    nready -= 1
                    if nready <= 0:
                        break

    def __close(self):
        for conn, user in enumerate(self.var.conection):
            # 主动退出所有账号，并记录数据
            self.service.local_var.record_list[user.user_account][1] += user.log_out()
            self.service.local_var.record_list[user.user_account][2] = False
            # 关闭所有连接
            conn.close()
        self.ser_sock.close()
        try:
            f = open(self.__database_location, 'w')
            json.dump(obj=self.service.local_var.record_list, fp=f)
        except:
            raise
        exit(0)

    def server_ctrl(self):
        while True:
            cmd = raw_input("press cmd to control server\n")
            if cmd == 'exit':
                c = raw_input('Are you sure to exit server program?\nPress "y" to continue, else to return\n')
                if c == 'y':
                    self.__exit_flag = True
                    return
            else:
                print("Invalid cmd, return")

    def welcome_program(self, conn):
        print ('Connected by', conn.getpeername())
        info = "Welcome!\nYou could log in, or sign up a new account"
        conn.sendall(info)


if __name__ == "__main__":
    s = Server()