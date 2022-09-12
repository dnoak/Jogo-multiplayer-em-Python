import threading
import socket
from turtle import update
import pygame
import timeit, time
import numpy as np
import os

os.system('cls')

server_socket_UDP = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_socket_UDP.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

host = 'localhost'
port_UDP = 1233


try:
    server_socket_UDP.bind((host, port_UDP))
except socket.error as e:
    print(str(e))


def player_thread_UDP():
    while True:
        print('Esperando client: ')
        keys, address = server_socket_UDP.recvfrom(64)
        # if
        server_socket_UDP.sendto(keys, address)
        print(keys, address)

#threading.Thread(target=player_thread_UDP).start()
player_thread_UDP()