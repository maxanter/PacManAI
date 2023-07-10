import pygame
from game import Game

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 576
human = True


def get_state(game):
    def search_for_position(position, position_old, position_new):
        x = round(position / position_old * position_new)
        if x < 0.5:
            x = 1
        return x

    enemys = 0
    state = []  # 170, 15
    state.append(search_for_position(game.player.rect.x, 576, 18))
    state.append(search_for_position(game.player.rect.y, 800, 25))
    state.append(0)
    state.append(1)
    state.append(2)
    state.append(3)
    state.append(len(game.dots_group.sprites()))
    for enemy in game.enemies.sprites():
        state.append(search_for_position(enemy.rect.x, 576, 18))
        state.append(search_for_position(enemy.rect.y, 800, 25))
        enemys += 1
    if enemys < 4:
        state.append(search_for_position(game.player.rect.x, 576, 18))
        state.append(search_for_position(game.player.rect.y, 800, 25))
    # for dot in game.dots_group.sprites():
    #    state.append(dot.rect.x)
    #    state.append(dot.rect.y)
    # 156
    print(state)

def main():

    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH,SCREEN_HEIGHT))
    pygame.display.set_caption("PACMAN")
    done = False
    clock = pygame.time.Clock()
    game = Game()
    while not done:
        get_state(game)
        done = game.process_events(1, human)
        reward, score, done = game.run_logic()
        game.display_frame(screen)
        clock.tick(30)
    pygame.quit()

if __name__ == '__main__':
    main()
