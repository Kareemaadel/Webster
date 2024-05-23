from socket import *
import os
import struct
import numpy as np
host='127.0.0.1'
port = 12345

sock=socket(AF_INET,SOCK_DGRAM)
sock.bind((host,port))
print("Reciever connected to ",host," port ",port)
seq_no=1
count=0

img=bytes()
while True:
    packet,s_address=sock.recvfrom(1032)
    # try:
    pack_id,file_id,tail=struct.unpack('!HHH',packet[:6])
    file=file_id
    pack_id=np.random.choice([pack_id,pack_id+4],p=[0.85,0.15])
    if(pack_id==seq_no):
        count+=1
        print('Packet',pack_id,' recieved')
        img+=packet[6:]
        ack=struct.pack('!HH',seq_no,file_id)
        sock.sendto(ack,s_address)
        seq_no+=1
        if(tail==0xFFFF):
            print("All sent! compiling code")
            print("Number of packets:", count)
            with open('rcv'+str(file)+'.jpeg','wb') as image:
                image.write(img)
            break
    else:
        print("ُError here")
        ack=struct.pack('!HH',seq_no-1,file_id)
        sock.sendto(ack,s_address)
    # except: print("Error recieving one of the packets")



