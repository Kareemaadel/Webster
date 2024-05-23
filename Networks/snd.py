import socket
import struct
import os
import random
import time

MSS = 1024
WINDOW_SIZE = 4
TIMEOUT_INTERVAL = 2

def send_file(filename, receiver_ip, receiver_port, file_id):
    sender_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    retransmission_count = 0
    start_time = time.time()
   
    with open(filename, "rb") as file:
        data = file.read()
        chunks = [data[i:i+MSS] for i in range(0, len(data), MSS)]
   
    base = 1
    seq_num = 1
    packets = []
    lost = []

    while seq_num <= len(chunks):
        while seq_num - base < WINDOW_SIZE:
            packet_id = seq_num % 65536
            packet_data = chunks[seq_num-1]
            trailer = 0xFFFF if seq_num == len(chunks) else 0x0000
            packet = struct.pack("!HHH", packet_id, file_id, trailer) + packet_data
            sender_socket.sendto(packet, (receiver_ip, receiver_port))
            packets.append((packet_id, time.time()))
            seq_num += 1
            print("Packet ID", packet_id, "sent")

        sender_socket.settimeout(TIMEOUT_INTERVAL)
        while True:
            try:
                ack, _ = sender_socket.recvfrom(1024)
                ack_packet_id = struct.unpack("!HH", ack)[0]
                if ack_packet_id >= base:
                    base = ack_packet_id + 1
                    break
            except socket.timeout:
                print("timeout occured")
                for i in range(base, seq_num):
                    packet_data = chunks[i-1]
                    trailer = 0xFFFF if i == len(chunks) - 1 else 0x0000
                    packet = struct.pack(">HHH", i, file_id, trailer) + packet_data
                    retransmission_count += 1
                    print("Packet", i, "sent again")
                    sender_socket.sendto(packet, (receiver_ip, receiver_port))
                    lost.append((i, time.time()))


    end_time = time.time()
    elapsed_time = end_time - start_time

    num_packets = len(packets)
    num_bytes = os.path.getsize(filename)
    
    avg_transfer_rate_bytes = num_bytes / elapsed_time
    avg_transfer_rate_packets = num_packets / elapsed_time

    print("File Transfer Information:")
    print("Start Time:", time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(start_time)))
    print("End Time:", time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(end_time)))
    print("Elapsed Time:", elapsed_time, "seconds")
    print("Number of Packets:", num_packets)
    print("Number of Bytes:", num_bytes)
    print("Number of Retransmissions (Sender):", retransmission_count)
    print("Average Transfer Rate (Bytes/sec):", avg_transfer_rate_bytes)
    print("Average Transfer Rate (Packets/sec):", avg_transfer_rate_packets)
    with open('plot'+str(file_id)+'.txt','w') as put:
            for i in packets:
                com_sep=str(i[0])+","+str(i[1])+"\n"
                put.writelines(com_sep)
    with open('lost'+str(file_id)+'.txt','w') as put:
            for i in lost:
                com_sep=str(i[0])+","+str(i[1])+"\n"
                put.writelines(com_sep) 
    sender_socket.close()

if __name__ == "__main__":
    filename = r"small file.jpeg"
    receiver_ip = "127.0.0.1"
    receiver_port = 12345
    send_file(filename, receiver_ip, receiver_port, 1)