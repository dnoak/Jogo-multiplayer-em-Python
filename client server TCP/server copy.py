from decimal import MAX_EMAX
import threading
import socket
import os
import numpy as np

with open('client server/client.py', 'rb') as client:
    update = client.read()

'''with open('client server/client_att.py', 'wb') as client:
    client.write(update)'''

ServerSocket = socket.socket()
host = '0.0.0.0'
port = 1233
player_count = 0

try:
    ServerSocket.bind((host, port))
except socket.error as e:
    print(str(e))

max_players = 4

player_list = []

print('Esperando Conexão..')
ServerSocket.listen(max_players)

syms = ['X','#','O','@']
coords = [[np.random.randint(1,10), np.random.randint(1,50)] for r in range(4)]
coords = np.random.random((max_players, 2))
print(coords)


'''def Player():
    def __init__(self, name, ip):
        self.name = name
        self.ip = ip

    def position(self, coords):'''



def threaded_client(connection, address, player_count):
    global coords

    connection.send(str.encode('Conectado.'))

    coord = coords[player_count]
    while True:
        if coord == [0,0]:
            return
        data = connection.recv(2048)
        reply = f'{address} ' + data.decode('utf-8')
        #print(reply)
        if not data:
            continue

        if data.decode() == 'w':
            coord[0] -= 1
        if data.decode() == 's':
            coord[0] += 1
        if data.decode() == 'd':
            coord[1] += 1
        if data.decode() == 'a':
            coord[1] -= 1

        coords_str = ''
        for c in range(len(coords)):
            if coord == coords[c] and c != player_count:
                coords[c] = [0, 0]
            print(coord, coords[c])

            coords[c][0] = coords[c][0]%10
            coords[c][1] = coords[c][1]%50
            coords_str += f'{coords[c][0]},{coords[c][1]} '
        #print(coords, coords_str)
        
        for cli in player_list:
            cli[0].sendall(str.encode(coords_str))

    connection.close()

for _ in range(max_players):
    client, address = ServerSocket.accept()
    player_list.append([client, address])

    print('Conectado em: ' + address[0] + ':' + str(address[1]))

    threading.Thread(target = threaded_client, args = (client, address, player_count, )).start()

    player_count += 1
    print('Player: ' + str(player_count))
ServerSocket.close()