import socket
import os
import timeit

os.system('cls')

HOST = '0.0.0.0'
PORT_UDP = 1234
SERVER_TICK_RATE = 60
MAX_PLAYERS = 4

server_socket_UDP = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_socket_UDP.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 1)

server_socket_UDP.bind((HOST, PORT_UDP))
print('Esperando Conexão..')

j1c = 0
j2c = 0

while True:
    
    j1a, j2a = ('127.0.0.1', 50000), ('127.0.0.1', 50001)

    received_data, received_address = server_socket_UDP.recvfrom(512)

    if received_address == j1a:
        j1c += 1

    if received_address == j2a:
        j2c += 1

    print(f'{100*(j1c/(j1c+j2c)):.0f}, {100*(j2c/(j1c+j2c)):.0f}')



