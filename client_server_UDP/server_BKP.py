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
        self.is_updated = False
    

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
    
        #self.is_updated = True
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
    #threading.Thread(target=thread_receive_data_from_players).start()
    while True:
        time_limit = False
        while not time_limit:
            initial_time = timeit.default_timer()

            received_data, received_address = server_socket_UDP.recvfrom(512)

            if not received_address:
                continue

            player_dict_is_not_full = len(players_dict) < MAX_PLAYERS
            player_does_not_exist = received_address not in players_dict

            if player_does_not_exist:
                if player_dict_is_not_full:
                    players_dict[received_address] = create_player(received_address)
                else: continue

            if not players_dict[received_address].is_updated:
                players_dict[received_address].data = pickle.loads(received_data)
                players_dict[received_address].is_updated = True
                #players_dict[received_address].update()

            elapsed_time = timeit.default_timer() - initial_time
            time_limit = elapsed_time > (1/SERVER_TICK_RATE)

        for all_address in players_dict:
            if players_dict[all_address].is_updated:
                players_dict[all_address].update()

        for updated_address in players_dict:
            if players_dict[updated_address].is_updated:
                for all_address in players_dict:
                    server_socket_UDP.sendto(
                        players_dict[received_address].to_UDP_data(),
                        all_address
                        )

        for all_address in players_dict:
            players_dict[all_address].is_updated = False

        print(f'{1/elapsed_time:.0f}')

        
    

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

