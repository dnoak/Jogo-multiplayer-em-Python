import threading
import socket
from xml.sax.handler import all_properties
import pygame
import timeit
import time
import pickle
import numpy as np
import os


class Player(pygame.sprite.Sprite):

    player_keys_dict = {
        'w': np.array([0,-1]),
        'a': np.array([-1,0]),
        's': np.array([0,+1]),
        'd': np.array([+1,0]),
        }

    def __init__(self, name, address, sprite, data):
        super().__init__()
        self.name = name
        self.address = address
        self.sprite = pygame.Surface((32,64))
        self.data = data

        self.UDP_pkg_count = 0

        self.rect = self.sprite.get_rect(center=(0,0))
        self.speed = 5

        self.shoot_sprite = pygame.Surface((20,10))
        self.shoot_rect = self.shoot_sprite.get_rect(center=(0,0))
        self.shoots_direction_list = []
        self.shoots_rect_list = []
        self.shoots_speed = 6
        self.reload_time = 1
        self.max_shoots = 2

        self.not_clicked = True
        self.is_not_updated = True
    

    def click_direction(self):
        if self.not_clicked:
            threading.Thread(
                target=self.shoot, 
                args=(self.data['click direction'],)
            ).start()
    
    def shoot(self, angle):
        self.not_clicked = False
        print(f"{self.name} Atirou na direção: {angle:.2f}°")

        if len(self.shoots_direction_list) > self.max_shoots - 1:
            del self.shoots_direction_list[0]
            del self.shoots_rect_list[0]

        rect_copy = self.rect.copy()
        x = rect_copy.x
        y = rect_copy.y
        x_inc = +np.cos(np.deg2rad(angle)) * self.shoots_speed
        y_inc = -np.sin(np.deg2rad(angle)) * self.shoots_speed
        #print(x_inc, y_inc)

        self.shoots_direction_list.append(np.array([[x, y], [x_inc, y_inc]]))
        self.shoots_rect_list.append(rect_copy)
        #print(self.shoots_rect_list)

        time.sleep(self.reload_time)
        self.not_clicked = True

    def to_UDP_data(self):
        data = {
            'address': self.address,
            'rect': self.rect,
            'shoots': self.shoots_rect_list,
            }
        return pickle.dumps(data)

    def update(self):

        self.rect.x += self.data['move direction'][0] * self.speed
        self.rect.y += self.data['move direction'][1] * self.speed

        if self.data['click direction']:
            #print(self.data['click direction'])
            self.click_direction()
    
        for shoot_rect, shoot_direction in zip(
            self.shoots_rect_list, self.shoots_direction_list
            ):

            #print(shoot_rect, shoot_direction)

            shoot_direction[0] += shoot_direction[1]
            shoot_rect.x = shoot_direction[0,0] 
            shoot_rect.y = shoot_direction[0,1] 
    
        #self.is_updated = False
        self.UDP_pkg_count = 0
        


def update_client(client, path):
    with open(path, 'rb') as client:
        update = client.read()
    client.send(update)


def create_player(address):
    global players_count

    player = Player(
        name = f'p{players_count}',
        address = address,
        sprite = f'sprites/p{players_count}.png',
        data = None,
    )
    print(f'Jogador {player.name} criado {player.address}.')

    players_count += 1
    return player



def thread_receive_data_from_players():
    global global_data_address
    global_data_address = None, None
    while True:
        global_data_address = server_socket_UDP.recvfrom(512)

def receive_data_from_players():
    global global_data_address
    threading.Thread(target=thread_receive_data_from_players).start()
    
    j1a, j2a = ('127.0.0.1', 50000), ('127.0.0.1', 50001)
    while True:
        j1p, j2p = 0, 0
        j1c, j2c = 0, 0
        
        tempo = 0
        t0 = timeit.default_timer()

        while (timeit.default_timer()-t0) < 1/60:
            addr = global_data_address[1]

            if addr == j1a:
                j1c += 1
                j1p = j1c/(j1c+j2c)

            if addr == j2a:
                j2c += 1
                j2p = j2c/(j1c+j2c)
            
            print(f'{100*j1p:.0f}, {100*j2p:.0f}')


        

        '''if not addr:
            continue
        
        if addr not in players_dict:
            players_dict[addr] = create_player(addr)
        
        if players_dict[addr].is_not_updated:
            players_dict[addr].UDP_pkg_count += 1
            for ad in players_dict:
                print(players_dict[ad].UDP_pkg_count, end=', ')
            print()
        else:
            continue


        clock.tick(5)
        for ad in players_dict:
            players_dict[ad].is_not_updated = True'''
        
        
        

    

if __name__ == '__main__':

    os.system('cls')

    HOST = '0.0.0.0'
    PORT_UDP = 1234
    SERVER_TICK_RATE = 60
    MAX_PLAYERS = 4

    server_socket_UDP = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_socket_UDP.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 1)

    clock = pygame.time.Clock()

    try:
        server_socket_UDP.bind((HOST, PORT_UDP))
        print('Esperando Conexão..')
        connected = True
    except socket.error as e:
        print(str(e))
        connected = False

    if connected:
        players_count = 0
        players_dict = {}
        receive_data_from_players()

