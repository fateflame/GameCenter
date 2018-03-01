import socket
import sys
import select


class Client:
    def __init__(self):
        self.cli_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def connect(self, addr, port):
        self.cli_sock.connect((addr, port))
        self.cli_main()

    def cli_main(self):
        while True:
            rset = [self.cli_sock, sys.stdin]

            r,w,x = select.select(rset, [], [], None)
            if self.cli_sock in r:
                data = self.cli_sock.recv(1024)
                if len(data) == 0:
                    print("server terminated prematurely")
                    exit(1)
                print(data)
            if sys.stdin in r:
                data = sys.stdin.readline()[:-1]
                if len(data) == 0:
                    return
                self.cli_sock.sendall(data)


if __name__ == "__main__":
    c = Client()
    c.connect("10.26.29.120", 10008)
