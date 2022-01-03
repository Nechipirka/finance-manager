import pygame
import sys


def events(character):
    """Обработка событий персонажа"""

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()
        elif event.type == pygame.KEYDOWN:
            # влево
            if event.key == pygame.K_a:
                character.mleft = True

            # вправо
            if event.key == pygame.K_d:
                character.mright = True

            # верх
            if event.key == pygame.K_w:
                character.mup = True

            # вниз
            if event.key == pygame.K_s:
                character.mdown = True

        elif event.type == pygame.KEYUP:
            # влево
            if event.key == pygame.K_a:
                character.mleft = False

            # вправо
            if event.key == pygame.K_d:
                character.mright = False

            # верх
            if event.key == pygame.K_w:
                character.mup = False

            # вниз
            if event.key == pygame.K_s:
                character.mdown = False


class Character():
    def __init__(self, screen):
        """Инициализация персонажа"""

        self.screen = screen
        self.image = pygame.image.load('character.png')
        self.rect = self.image.get_rect()
        self.screen_rect = screen.get_rect()
        self.rect.centerx = self.screen_rect.centerx
        self.rect.bottom = self.screen_rect.bottom

        self.mright = False
        self.mleft = False
        self.mup = False
        self.mdown = False

    def output(self):
        """Рисование персонажа"""

        self.screen.blit(self.image, self.rect)

    def update_character(self):
        """Обновление позиции персонажа"""

        # влево
        if self.mleft and self.rect.left > 0:
            self.rect.centerx -= 1
            print((self.rect.centerx - 1), (self.rect.centery))

        # вправо
        if self.mright and self.rect.right < self.screen_rect.right:
            self.rect.centerx += 1
            print((self.rect.centerx + 1), (self.rect.centery))

        # верх
        if self.mup and self.rect.centerx > 0:
            self.rect.centery -= 1
            print((self.rect.centerx), (self.rect.centery - 1))

        # вниз
        if self.mdown and self.rect.bottom < self.screen_rect.bottom:
            self.rect.centery += 1
            print((self.rect.centerx), (self.rect.centery + 1))
