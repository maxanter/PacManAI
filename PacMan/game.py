
import pygame
from player import Player
from enemies import *
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 576

BLACK = (0,0,0)
WHITE = (255,255,255)
BLUE = (0,0,255)
RED = (255,0,0)

class Game(object):
    def __init__(self):
        self.font = pygame.font.Font(None,40)
        self.about = False
        self.game_over = True
        self.score = 0
        self.font = pygame.font.Font(None,35)
        self.player = Player(32,32,"player.png")
        self.horizontal_blocks = pygame.sprite.Group()
        self.vertical_blocks = pygame.sprite.Group()
        self.dots_group = pygame.sprite.Group()
        self.pause = False
        for i,row in enumerate(enviroment()):
            for j,item in enumerate(row):
                if item == 1:
                    self.horizontal_blocks.add(Block(j*32+8,i*32+8,BLACK,16,16))
                elif item == 2:
                    self.vertical_blocks.add(Block(j*32+8,i*32+8,BLACK,16,16))
        self.enemies = pygame.sprite.Group()
        self._place_enemies()
        self._place_dots()

        self.pacman_sound = pygame.mixer.Sound("pacman_sound.ogg")
        self.game_over_sound = pygame.mixer.Sound("game_over_sound.ogg")

    def reset(self):
        self.score = 0
        self.enemies.empty()
        self._place_enemies()
        self.dots_group.empty()
        self._place_dots()
        self.player.rect.topleft = (32,128)

    def _place_dots(self):
        for i, row in enumerate(enviroment()):
            for j, item in enumerate(row):
                if item != 0:
                    self.dots_group.add(Ellipse(j*32+12,i*32+12,WHITE,8,8))

    def _place_enemies(self):
        self.enemies.add(Slime(288, 96, 0, 2))
        self.enemies.add(Slime(288, 320, 0, -2))
        self.enemies.add(Slime(544, 128, 0, 2))
        self.enemies.add(Slime(32, 224, 0, 2))

    def _place_player(self):
        self.player = Player(32, 128, "player.png")

    def process_events(self, action1, human):
        if self.game_over and not self.about:
                self.__init__()
                self.game_over = False
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return True



            if human:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RIGHT:
                        self.player.move_right()

                    elif event.key == pygame.K_LEFT:
                        self.player.move_left()

                    elif event.key == pygame.K_UP:
                        self.player.move_up()

                    elif event.key == pygame.K_DOWN:
                        self.player.move_down()

                    elif event.key == pygame.K_ESCAPE:
                        self.game_over = True
                        self.about = False
                    elif event.key == pygame.K_0:
                        self.reset()

                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_RIGHT:
                        self.player.stop_move_right()
                    elif event.key == pygame.K_LEFT:
                        self.player.stop_move_left()
                    elif event.key == pygame.K_UP:
                        self.player.stop_move_up()
                    elif event.key == pygame.K_DOWN:
                        self.player.stop_move_down()

                elif event.type == pygame.MOUSEBUTTONDOWN:
                    self.player.explosion = True


        if human == False:
            action = 0
            for i in range(len(action1)):
                if action1[i] == 1:
                    action = i
            if action == 0:
                self.player.move_right()
            elif action == 1:
                self.player.move_left()
            elif action == 2:
                self.player.move_up()
            elif action == 3:
                self.player.move_down()
        return False



    def run_logic(self):
        done = False
        reward = 0
        if not self.game_over:
            self.player.update(self.horizontal_blocks,self.vertical_blocks)
            block_hit_list = pygame.sprite.spritecollide(self.player,self.dots_group,True)
            if len(block_hit_list) > 0:
                self.pacman_sound.play()
                self.score += 1
                reward = 10
                if len(self.dots_group.sprites()) < len(self.dots_group.sprites())/2*1.5:
                    reward = 11
                if len(self.dots_group.sprites()) < len(self.dots_group.sprites())/2:
                    reward = 15
                if len(self.dots_group.sprites()) < len(self.dots_group.sprites())/4:
                    reward = 20
                if len(self.dots_group.sprites()) == 0:
                    reward = 100
            block_hit_list = pygame.sprite.spritecollide(self.player,self.enemies,True)
            if len(block_hit_list) > 0:
                self.player.explosion = True
                self.game_over_sound.play()
                done = True
                reward = -300
            self.game_over = self.player.game_over
            self.enemies.update(self.horizontal_blocks,self.vertical_blocks)

        return reward, self.score, done

    def display_frame(self,screen):
        screen.fill(BLACK)
        if self.game_over:
            if self.about:
                self.display_message(screen,"It is an arcade Game")
        else:
            self.horizontal_blocks.draw(screen)
            self.vertical_blocks.draw(screen)
            draw_enviroment(screen)
            self.dots_group.draw(screen)
            self.enemies.draw(screen)
            screen.blit(self.player.image,self.player.rect)
            text = self.font.render("Score: " + str(self.score),True,GREEN)
            screen.blit(text,[120,20])

        pygame.display.flip()

    def display_message(self,screen,message,color=(255,0,0)):
        label = self.font.render(message,True,color)
        width = label.get_width()
        height = label.get_height()
        posX = (SCREEN_WIDTH /2) - (width /2)
        posY = (SCREEN_HEIGHT /2) - (height /2)
        screen.blit(label,(posX,posY))
