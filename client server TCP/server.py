import threading
import socket
from turtle import update
import pygame
import timeit, time
import numpy as np
import os

os.system('cls')

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
host = 'localhost'
port = 1233
players_count = 0

clock = pygame.time.Clock()

try:
    server_socket.bind((host, port))
except socket.error as e:
    print(str(e))

max_players = 1

players_list = []

print('Esperando Conexão..')
server_socket.listen(max_players)

class Player(pygame.sprite.Sprite):
    player_keys_dict = {
        'w': np.array([0,-1]),
        'a': np.array([-1,0]),
        's': np.array([0,+1]),
        'd': np.array([+1,0]),
    }
    def __init__(self, name, address, color, random_pos):
        super().__init__()
        self.name = name
        self.address = address
        self.image = pygame.Surface((32,64))
        self.image.fill(color)
        self.rect = self.image.get_rect(topleft = [0,0])

        self.direction = pygame.math.Vector2(0,0)
        self.speed = 1

    def move(self, player_input):
        for key in player_input:
            self.direction += self.player_keys_dict[key] * self.speed
        print(self.direction)

    def update(self):
        self.rect.x = self.direction[0]
        self.rect.y = self.direction[1]
        return self.rect


def update_client(connection, path):
    with open(path, 'rb') as client:
        update = client.read()
    connection.send(update)

def player_thread(connection, address):
    global players_count

    #update_client(connection, 'client server/client.py') 
    #return
    
    player_name = 'p1' #input('Nome: ')
    player_color = 'red' #input('Cor: ')
    player_init_position = np.random.random(2)
    player = Player(player_name, address, player_color, player_init_position)

    players_list.append(player)

    # garante que todos os jogadores estão conectados e o jogo inicia ao mesmo tempo para todos.
    timer0 = timeit.default_timer()
    t0 = 0
    while players_count < max_players:
        t1 = int(timeit.default_timer() - timer0)
        if t1 != t0:
            connection.send(str.encode(f'Esperando mais {max_players - players_count} jogadores ({t1}s).'))
            t0 = t1

    connection.send(str.encode(f'Conectado.'))

    while True:
        player_input = connection.recv(32).decode().split(',')[:-1]
        player.move(player_input)
        player.update()

        connection.send(str.encode(f'{player.rect.x},{player.rect.y}'))


    connection.close()

for _ in range(max_players):
    client, address = server_socket.accept()
    #players_list.append([client, address])
    
    print('Conectado em: ' + address[0] + ':' + str(address[1]))
    #client.send(str.encode(f'Conectado'))

    threading.Thread(target = player_thread, args=(client,address,)).start()


    players_count += 1
    print('Player: ' + str(players_count))
server_socket.close()