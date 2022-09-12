import socket
import threading
import pygame
import time
import sys
import os

os.system('cls')

pygame.init()
resX, resY = 800, 500
screen = pygame.display.set_mode((resX,resY))
pygame.display.set_caption('Jogo')
clock = pygame.time.Clock()

player_sprite = pygame.image.load('jogo teste/player.png').convert_alpha()
player_sprite = pygame.transform.scale(player_sprite, (50, 50))
player_rect = player_sprite.get_rect(midbottom = (100, 100) )


client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
client_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

host = 'localhost'
port = 1233

print('Esperando Conexão..')
try:
    client_socket.connect((host, port))
except socket.error as e:
    print(str(e))

Response = client_socket.recv(2048)
print(Response.decode())


def thread_server_response():
    while True:
        
        
        response = client_socket.recv(64).decode()
        print(response)

        

        #player_rect = response

        screen.blit(player_sprite, player_rect)

        pygame.display.update()
        clock.tick(60)


    
def client_send():
    while True:
        player_input_str = ''

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        
        keys = pygame.key.get_pressed()
    
        if keys[pygame.K_w]:
            player_input_str += 'w,'
        if keys[pygame.K_a]:
            player_input_str += 'a,'
        if keys[pygame.K_s]:
            player_input_str += 's,'
        if keys[pygame.K_d]:
            player_input_str += 'd,'

        #if player_input_str:
            #print(player_input_str)

        #time.sleep(1)
        client_socket.send(str.encode(player_input_str))

       
        #player_rect.x = 50
        #player_rect.y = 50

        
threading.Thread(target=thread_server_response).start()
client_send()

client_socket.close()