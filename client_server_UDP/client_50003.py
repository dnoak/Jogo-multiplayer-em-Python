import socket
import threading
import timeit
import pygame
import numpy as np
import time
import pickle
import sys
import re
import os


os.system('cls')

# pygame
pygame.init()
resX, resY = 500, 500

screen = pygame.display.set_mode((resX,resY))
ceu = pygame.image.load('map/ceu.jpg').convert_alpha()
chao = pygame.image.load('map/chao.png').convert_alpha()
font = pygame.font.Font(None, 50)

pygame.display.set_caption('Jogo')
clock = pygame.time.Clock()
FPS_input = 60
FPS_screen = 60

class Player(pygame.sprite.Sprite):
    def __init__(self, name, address, sprite):
        self.name = name
        self.address = address
        self.sprite = pygame.image.load(sprite).convert_alpha()

        self.sprite =  pygame.transform.scale(self.sprite, (50, 100))
        self.rect = self.sprite.get_rect(midbottom = (100, 100) )

    def update(self):
        self.rect = self.buffer


client_socket_UDP = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
# impede o delay do buffer
client_socket_UDP.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 1)

host = 'localhost'
port_LOCAL = int(re.findall(r'\d+', os.path.basename(__file__))[0])
port_SERVER = 1234


print('Esperando Conexão..')
try:
    client_socket_UDP.bind((host, port_LOCAL))
except socket.error as e:
    print(str(e))

#Response = client_socket_TCP.recv(2048)
#print(Response.decode())

players_list = []
players_count = 0

def create_player(address):
    global players_count

    player_name = f'p{players_count}'
    player_address = address
    player_sprite = f'sprites/p{players_count}.png'
    
    players_count += 1
    
    player = Player(player_name, player_address, player_sprite)
    print(f'Jogador {player.name} criado - {player.address}')


    return player


def thread_screen_update():
    global FPS_input, FPS_screen, real_FPS_input
    real_FPS_screen = 1
    real_FPS_input = 1
    while True:
        t0 = timeit.default_timer()

        FPS_screen_text = font.render(f'{real_FPS_screen:.0f} FPS', False, 'black')
        FPS_input_text = font.render(f'{real_FPS_input:.0f} FPS', False, 'black')

        screen.blit(ceu, (0,0))
        screen.blit(chao, (0,330))
    
        for player in players_list:
            #player.update()
            screen.blit(player.sprite, player.rect)

        screen.blit(FPS_screen_text, (10,10))
        screen.blit(FPS_input_text, (10,50))
           
        pygame.display.update()

        clock.tick(FPS_screen)
        real_FPS_screen = 1/(timeit.default_timer() - t0)


def thread_server_response():
    while True:
        data, _ = client_socket_UDP.recvfrom(512)
        data = data.split(b';')

        try:
            address = pickle.loads(data[1])
            rect = pickle.loads(data[0])
        except:
            print(Exception)
            continue

        addr_not_in_player_list = address not in [p.address for p in players_list]
        if addr_not_in_player_list:
            players_list.append(create_player(address))
        
        for player in players_list:
            if player.address == address:
                player.rect = rect

def bot_player_movement(cont, length, keys):
    
    if cont >= length - 1: cont = 0
    else: cont += 1
    bot_input = keys[cont // (length//4)]

    return cont, bot_input


def client_send():
    global FPS_input, FPS_screen, real_FPS_input
    cont = 0
    while True:
        t0 = timeit.default_timer()

        player_input_list = [' ',' ',' ',' ']

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        
        keys = pygame.key.get_pressed()

        if keys[pygame.K_w]:
            player_input_list[0] = 'w'
        if keys[pygame.K_a]:
            player_input_list[1] = 'a'
        if keys[pygame.K_s]:
            player_input_list[2] = 's'
        if keys[pygame.K_d]:
            player_input_list[3] = 'd'
        
        if keys[pygame.K_EQUALS]:
            FPS_screen += 1
        if keys[pygame.K_MINUS]:
            FPS_screen -= 1
        
        if keys[pygame.K_LEFTBRACKET]:
            FPS_input += 1
        if keys[pygame.K_RIGHTBRACKET]:
            FPS_input -= 1
        
        cont, player_input_list = bot_player_movement(cont, 300, ['sd','a','wd','a'])

        player_input_str = ''.join(player_input_list)
    
        if player_input_str:
            client_socket_UDP.sendto(str.encode(player_input_str), (host, port_SERVER))

        clock.tick(FPS_input)

        real_FPS_input = 1/(timeit.default_timer() - t0)
 
threading.Thread(target=thread_server_response).start()
threading.Thread(target=thread_screen_update).start()
client_send()