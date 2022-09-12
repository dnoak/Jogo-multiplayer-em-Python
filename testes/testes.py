import numpy as np
import pygame

# server

player_pos = np.array([0, 0])

recv_keys = ''.split(',')[:-1]

player_keys_dict = {
    'w': np.array([0, -1]),
    'a': np.array([-1, 0]),
    's': np.array([0, 1]),
    'd': np.array([1, 0]),
}


for key in recv_keys:
    player_pos += player_keys_dict[key]

print(player_pos)

xx = [[1,10], [2,20], [3,30]]

print(xx[:][0])