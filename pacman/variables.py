import pygame,json
pygame.init()

UP = 0
DOWN = 1
LEFT = 2
RIGHT = 3

pygame.mixer.music.load('music.wav')
die = pygame.mixer.Sound('die.wav')
eat = pygame.mixer.Sound('eat.wav')
hit = pygame.mixer.Sound('hit.wav')
lost = pygame.mixer.Sound('lost.wav')
walk = pygame.mixer.Sound('walk.wav')