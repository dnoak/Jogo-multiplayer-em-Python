import socket
import threading
import pygame
import time
import sys
import os

os.system('cls')

client_socket_UDP = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
client_socket_UDP.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
host = 'localhost'
port_UDP = 1233

try:
    client_socket_UDP.bind((host, port_UDP))
except socket.error as e:
    print(str(e))

def thread_server_response():
    while True:
        data, address = client_socket_UDP.recvfrom(64)
        print(data, address)

def client_send():
    while True:
        player_input_str = input('Texto: ')

        client_socket_UDP.sendto(str.encode(player_input_str), (host, port_UDP))


threading.Thread(target=thread_server_response).start()
client_send()
