import time
import socket
import json
import base64
import struct
import const
from string import ascii_letters, digits
from itertools import product

class Slave:
    def __init__(self):
        self.port = 8000
        self.host = '127.0.0.1'
        self.slaves=[]
        self.n_slaves=1

    def connect(self):    
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((self.host, self.port))
        print("Connected to" , self.host,":",self.port, " in ", self.sock)
        
        """SOCKETS MULTICAST DE ENVIO"""
        
        self.sock_multicast_send = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        self.sock_multicast_send.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, self.MULTICAST_TTL)
        msg_connect = json.dumps({"command":"register"}).encode('utf-8')

        self.sock_multicast_send.sendto(msg_connect, (self.MCAST_GRP, self.MCAST_PORT))


    def send_msg(self, msg,conn):
        conn.send(msg)

    def encode64(self,password) -> str:
        string_pass = ('root:'+password).encode('utf-8')
        pass_64 = base64.b64encode(string_pass).decode('utf-8')
        return pass_64


    def combinations(self, length):
        lst=[]
        for i in product(ascii_letters + digits, repeat=length):
            lst.append(''.join(i))
        return lst
    
    
    def rcv_from_slaves(self):
        """create multicast sockets to receivedata"""
        
        #IS_ALL_GROUPS = True
        self.sock_multicast_receive = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        self.sock_multicast_receive.settimeout(0)                
        self.sock_multicast_receive.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        #if IS_ALL_GROUPS:
            # on this port, receives ALL multicast groups
        self.sock_multicast_receive.bind(('', self.MCAST_PORT))
        #else:
            # on this port, listen ONLY to MCAST_GRP
            #self.sock_multicast_receive.bind((self.MCAST_GRP, self.MCAST_PORT))
        
        mreq = struct.pack("4sl", socket.inet_aton(self.MCAST_GRP), socket.INADDR_ANY)

        self.sock_multicast_receive.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
    
    


    def loop(self):
        self.rcv_from_slaves()
        time.sleep(5)
        comb = self.combinations(const.PASSWORD_SIZE)
        i=0
        while True:
            """HTTP protocol and turn sockets on"""
            try:
                json_string = self.sock_multicast_receive.recv(10240).decode('utf-8')
                message = json.loads(json_string)
                if message['command'] == 'register':
                    self.n_slaves+=1
                    print("Number slaves:" ,self.n_slaves)
                elif message['command'] == 'found':
                    print(message)
                    self.sock_multicast_receive.close()
                    self.sock_multicast_send.close()
                    self.sock.close()
                    break
            except socket.error:
                pass
                    
            self.msg= "GET / HTTP/1.1\nHost: "+self.host+" : "+str(self.port)+"\n"
            self.msg += "Authorization: Basic "+str(self.encode64(comb[i]))+"\n\n"
            self.send_msg(self.msg.encode('utf-8'),self.sock)
                
            received=self.sock.recv(1024).decode('utf-8')

            if "OK" in received:
                msg_ok = {'command': 'found', 'password': comb[i]}
                msg_ok_encode=json.dumps(msg_ok).encode('utf-8')
                self.sock_multicast_send.sendto(msg_ok_encode, (self.MCAST_GRP, self.MCAST_PORT))
                print(msg_ok)
                break
            elif (received[-1] == "\n"):
                b=self.sock.recv(1024).decode('utf-8')
                received+=b
            print("Trying... ", comb[i])
            i+=1
            if (i%const.MIN_TRIES==0 and i!=0):
                time.sleep((const.COOLDOWN_TIME/1000)%60)
            
if __name__ == "__main__":
    s = Slave()
    s.connect()
    s.loop()

#while True:
#    print("all your base are belong to us")
#    time.sleep(1)