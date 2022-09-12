from turtle import speed
import pygame
import sys
import timeit

pygame.init()
resX, resY = 800, 500
screen = pygame.display.set_mode((resX,resY))
pygame.display.set_caption('Jogo')
clock = pygame.time.Clock()

test_font = pygame.font.Font(None, 50)
texto = test_font.render('Jogo online', False, 'black')

ceu = pygame.image.load('ceu.jpg').convert_alpha()
chao = pygame.image.load('chao.png').convert_alpha()

player = pygame.image.load('player.png').convert_alpha()
player = pygame.transform.scale(player, (player.get_size()[0]/10, player.get_size()[1]/10))
player_w, player_h = player.get_size()[0], player.get_size()[1]
player_g = 0
gravidade = -25

player_rect = player.get_rect(midbottom = (100, player_h) )

pos = [0,0] 
invX, invY = 0, 0
timer_f = 0
speedX, speedY = 5, 3

while True:
    timer_i = timeit.default_timer()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_w and player_rect.bottom == 360:
                player_g = gravidade
                print('Pulo', player_g)


        mouse_pos = pygame.mouse.get_pos()
        if event.type == pygame.BUTTON_LEFT:
            #if player_rect.collidepoint(mouse_pos):
            print('Clicou')
            player_rect.left = mouse_pos[0]
            player_rect.bottom = mouse_pos[1]

        if event.type == pygame.MOUSEWHEEL:
            speedX -= 1
        if event.type == pygame.BUTTON_WHEELUP:
            speedX += 1
        print(speedX)

    texto = test_font.render(f'{timer_f:.0f} FPS', False, 'black')
    
    screen.blit(ceu, (0,0))
    screen.blit(chao, (0,330))
    screen.blit(texto, (100,0))
    
    player_rect.x += speedX*(invX - (not invX))
    invX = (invX +  (player_rect.x )//(resX) )%2

    player_g += 1
    player_rect.y += player_g

    player_rect.y += speedY*(invY - (not invY))
    invY = (invY +  (player_rect.y )//(resY) )%2

    if player_rect.bottom >= 360:
        player_rect.bottom = 360
        player_g = gravidade

    screen.blit(player, player_rect)

    mouse_pos = pygame.mouse.get_pos()


    pygame.display.update()
    clock.tick(60)
    
    timer_f = round(1/(timeit.default_timer() - timer_i))


    
