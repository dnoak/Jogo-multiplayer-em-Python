import pygame

class Player(pygame.sprite.Sprite):
    def __init__(self, pos):
        super().__init__()
        self.image = pygame.Surface((32,64))
        self.image.fill('red')
        self.rect = self.image.get_rect(topleft = pos)

        self.direction = pygame.math.Vector2(0,0)
        self.speed = 8
        self.gravity = 0.8
        self.jump_speed = -10
    
    def get_input(self):
        keys = pygame.key.get_pressed()
        #print(keys[pygame.K_d], keys[pygame.K_a])

        keyD = keys[pygame.K_d]
        keyA = keys[pygame.K_a]
        keySPC = keys[pygame.K_SPACE]

        self.direction.x = 0

        if keyD and not keyA:
            self.direction.x = 1
        if keyA and not keyD:
            self.direction.x = -1
        if keySPC:
            self.jump()
    
    def jump(self):
        self.direction.y = self.jump_speed
    
    def apply_gravity(self):
        self.direction.y += self.gravity
        self.rect.y += self.direction.y

    def update(self):
        self.get_input()
        self.rect.x += self.direction.x*self.speed
        self.apply_gravity()