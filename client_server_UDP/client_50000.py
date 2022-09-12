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

class Shoot(pygame.sprite.Sprite):
    def __init__(self, sprite):
        self.sprite = pygame.image.load(sprite).convert_alpha()
        self.sprite =  pygame.transform.scale(self.sprite, (20, 10))

        self.shoots_rect_list = []

class Player(pygame.sprite.Sprite):
    def __init__(self, name, address, sprite):

        self.name = name
        self.address = address
        self.sprite = pygame.image.load(sprite).convert_alpha()
        self.sprite =  pygame.transform.scale(self.sprite, (50, 100))
        self.rect = self.sprite.get_rect(center = (0, 0))

        self.shoot_sprite = pygame.image.load(sprite).convert_alpha()
        self.shoot_sprite =  pygame.transform.scale(self.sprite, (5, 10))
        self.shoots_rect_list = []


def thread_screen_update():
    global FPS_input, FPS_screen, real_FPS_input
    real_FPS_screen = 1
    real_FPS_input = 1
    
    while True:
        t0 = timeit.default_timer()

        FPS_screen_text = font.render(f'FPS (Tela) : {FPS_screen} - {real_FPS_screen:.0f}', False, 'black')
        FPS_input_text = font.render(f'FPS (Input): {FPS_input} - {real_FPS_input:.0f}', False, 'black')

        screen.blit(ceu, (0,0))
        screen.blit(chao, (0,330))
    
        for address in players_dict:
            screen.blit(players_dict[address].sprite, players_dict[address].rect)
            for shoot_rect in players_dict[address].shoots_rect_list:
                screen.blit(players_dict[address].shoot_sprite, shoot_rect)
        #screen.blit()

        screen.blit(FPS_screen_text, (10,10))
        screen.blit(FPS_input_text, (10,40))
        
        pygame.display.update()

        clock.tick(FPS_screen)
        real_FPS_screen = 1/(timeit.default_timer() - t0)


def create_player(address):
    global players_count

    player = Player(
        name = f'p{players_count}',
        address = address,
        sprite = f'sprites/p{players_count}.png'
    )
    print(f'Jogador {player.name} criado {player.address}.')

    players_count += 1
    return player


def thread_server_response():
    while True:
        #try:
        UDP_data = pickle.loads(client_socket_UDP.recvfrom(512)[0])
        #except:
        #continue

        #print(UDP_data['address'])
        if UDP_data['address'] not in players_dict:
            players_dict[UDP_data['address']] = create_player(UDP_data['address'])
        
        players_dict[UDP_data['address']].rect = UDP_data['rect']
        players_dict[UDP_data['address']].shoots_rect_list = UDP_data['shoots']


def bot_movement(cont, length, directions):
    global FPS_input, FPS_screen, real_FPS_input

    t0 = timeit.default_timer()

    if cont >= length - 1: cont = 0
    else: cont += 1

    clock.tick(FPS_input)
    real_FPS_input = 1/(timeit.default_timer() - t0)

    return cont, {
        'move direction': directions[cont // (length//4)],
        'click direction': None
        }


def player_inputs():
    global FPS_input, FPS_screen, real_FPS_input

    t0 = timeit.default_timer()

    mouse_pressed = False
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    mouse_direction = None
    if pygame.mouse.get_pressed()[0]:
        mouse_click_position = pygame.mouse.get_pos()
        player_position = players_dict[(HOST, PORT_LOCAL)].rect
        mouse_direction = -np.arctan2(
            mouse_click_position[1] - player_position.y,
            mouse_click_position[0] - player_position.x
            ) * 180 / np.pi
    
    keys = pygame.key.get_pressed()
    
    move_direction = np.array([0, 0])
    
    player_movement_dict = {
        'w': np.array([0,-1]),
        'a': np.array([-1,0]),
        's': np.array([0,+1]),
        'd': np.array([+1,0]),
        }

    if keys[pygame.K_w]:
        move_direction += player_movement_dict['w']
    if keys[pygame.K_a]:
        move_direction += player_movement_dict['a']
    if keys[pygame.K_s]:
        move_direction += player_movement_dict['s']
    if keys[pygame.K_d]:
        move_direction += player_movement_dict['d']
    
    if keys[pygame.K_EQUALS]:
        FPS_screen += 1
    if keys[pygame.K_MINUS]:
        FPS_screen -= 1
    
    if keys[pygame.K_LEFTBRACKET]:
        FPS_input += 1
    if keys[pygame.K_RIGHTBRACKET]:
        FPS_input -= 1
    
    clock.tick(FPS_input)
    real_FPS_input = 1/(timeit.default_timer() - t0)

    inputs_dict = {
        'move direction': move_direction,
        'click direction': mouse_direction
    }

    #if np.any(inputs_dict['move direction']) or inputs_dict['click direction']:
    return inputs_dict


def client_send():
    cont = 0
    while True:
        inputs = player_inputs()
        #cont, inputs = bot_movement(cont, 300, np.array([[1,0],[0,1],[-1,0],[0,-1]]))
    
        client_socket_UDP.sendto(pickle.dumps(inputs), (HOST, PORT_SERVER))
 
        
if __name__ == '__main__':

    os.system('cls')

    pygame.init()
    resX, resY = 500, 500

    screen = pygame.display.set_mode((resX,resY))
    ceu = pygame.image.load('map/ceu.jpg').convert_alpha()
    chao = pygame.image.load('map/chao.png').convert_alpha()
    font = pygame.font.Font(None, 35)

    pygame.display.set_caption('Jogo')
    clock = pygame.time.Clock()

    FPS_input = 60
    FPS_screen = 60

    client_socket_UDP = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    client_socket_UDP.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 1)

    HOST = '127.0.0.1'
    PORT_LOCAL = int(re.findall(r'\d+', os.path.basename(__file__))[0])
    PORT_SERVER = 1234

    print('Esperando Conexão..')
    try:
        client_socket_UDP.bind((HOST, PORT_LOCAL))
    except socket.error as e:
        print(str(e))

    players_count = 0
    players_dict = {(HOST, PORT_LOCAL): create_player((HOST, PORT_LOCAL))}

    threading.Thread(target=thread_server_response).start()
    threading.Thread(target=thread_screen_update).start()
    client_send()