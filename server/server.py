# -*- coding:utf-8 -*-
import socket
import select
import data_structure
import ConfigParser
import thread
import service
import threading


class Value:            # 服务器状态数据
    def __init__(self):
        self.conection = {}  # <sock, User> map to record the state of each connection


class Server:

    def __init__(self, f='./config'):
        self.config = f
        self.__load_config()

        self.var = Value()
        self.service = service.Service(self.__record_location)

        self.ser_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.ser_sock.bind((self.__host, self.__port))
        # 启动一个线程控制服务器
        t = threading.Thread(target=self.listen, args=[])
        try:
            t.start()
            self.server_ctrl()
            # TODO 暂停或关闭t，更新数据后退出
        except KeyboardInterrupt:
            self.__close()
            exit(0)

    def __load_config(self):
        cf = ConfigParser.ConfigParser()
        cf.read(self.config)

        self.__port = cf.getint('server', 'port')
        self.__host = cf.get('server', 'host')
        self.__backlog = cf.getint('server', 'backlog')
        self.__record_location = cf.get('server', 'database_location')

    def listen(self):
        self.ser_sock.listen(self.__backlog)

        while True:
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
                        conn.sendall(data)
                    nready -= 1
                    if nready <= 0:
                        break

    def __close(self):
        for conn in self.var.conection.keys():
            #self.var.conection[conn].close()
            # 关闭所有连接
            conn.close()
        self.ser_sock.close()
        exit(0)

    def server_ctrl(self):
        while True:
            cmd = raw_input("press cmd to control server\n")
            if cmd == 'exit':
                c = raw_input('Are you sure to exit server program?\nPress "y" to continue, else to return\n')
                if c == 'y':
                    return
            else:
                print("Invalid cmd, return")

    def welcome_program(self, conn):
        print ('Connected by', conn.getpeername())
        info = "Welcome!\nYou could log in, or sign up a new account"
        conn.sendall(info)


if __name__ == "__main__":
    s = Server()