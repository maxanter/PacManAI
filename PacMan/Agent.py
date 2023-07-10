import torch
import random
import numpy as np
import pygame
from collections import deque
from game import Game
from model import Linear_QNet, QTreiner
from helper import plot

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 576

MAX_MEMORY = 100_000
BATCH_SIZE = 1000
LR = 0.001

human = False
load_model = False

class Agent:
    def __init__(self):
        self.n_games = 0
        self.epsilon = 0
        self.gamma = 0.9
        self.memory = deque(maxlen=MAX_MEMORY)

        self.model = Linear_QNet(19, 256, 4)
        self.treiner = QTreiner(self.model, lr=LR, gamma=self.gamma)

        if load_model:
            self.model.load()




    def get_state(self,game):
        def search_for_position(position, position_old, position_new):
            x = round(position/ position_old * position_new)
            if x < 0.5:
                x = 1
            return x
        enemys = 0
        state = [] # 170, 15

        e_x_1 = 0
        e_y_1 = 0
        e_x_2 = 0
        e_y_2 = 0

        x = search_for_position(game.player.rect.x, 576, 18)
        y = search_for_position(game.player.rect.y, 800, 25)
        state.append(x)
        state.append(y)
        state.append(0)
        state.append(1)
        state.append(2)
        state.append(3)
        state.append(len(game.dots_group.sprites()))

        for enemy in game.enemies.sprites():
            state.append(search_for_position(enemy.rect.x, 576, 18))
            state.append(search_for_position(enemy.rect.y, 800, 25))
            enemys +=1

        if enemys < 4:
            state.append(search_for_position(game.player.rect.x, 576, 18))
            state.append(search_for_position(game.player.rect.y, 800, 25))
        for enemy in game.enemies.sprites():
            enemy_x = search_for_position(enemy.rect.x, 576, 18)
            enemy_y = search_for_position(enemy.rect.y, 800, 25)

            if y in range(enemy_y - 1, enemy_y + 1):
                if x + 1 == enemy_x or x + 2 == enemy_x or x + 23 == enemy_x:
                    e_x_1 = 1

                if x - 1 == enemy_x or x - 2 == enemy_x or x - 23 == enemy_x:
                    e_x_2 = 1

            if x in range(enemy_x - 1, enemy_x + 1):
                if y + 1 == enemy_y or y + 2 == enemy_y or y + 16 == enemy_y:
                    e_y_1 = 1

                if y + 1 == enemy_y or y + 2 == enemy_y or y + 16 == enemy_y:
                    e_y_2 = 1

        state.append(e_x_1)
        state.append(e_x_2)
        state.append(e_y_1)
        state.append(e_y_2)
        #for dot in game.dots_group.sprites():
        #    state.append(dot.rect.x)
        #    state.append(dot.rect.y)
            #156
        #print(state)

        return np.array(state, dtype=int)

    def remember(self, state, action, reward, next_state, done):
        self.memory.append((state, action, reward, next_state, done))

    def train_long_memory(self):
        if len(self.memory) > BATCH_SIZE:
            mini_sample = random.sample(self.memory, BATCH_SIZE)
        else:
            mini_sample = self.memory

        states, actions, rewards, next_states, dones = zip(*mini_sample)
        self.treiner.train_step(states, actions, rewards, next_states, dones)

    def train_short_memory(self, state, action, reward, next_state, done):
        self.treiner.train_step(state, action, reward, next_state, done)

    def get_action(self, state):
        self.epsilon = 80 - self.n_games
        if self.epsilon <= 0 or load_model == True:
            self.epsilon = 0.1
        final_move = [0,0,0,0]
        if random.randint(0,200) < self.epsilon:
            move = random.randint(0,3)
            final_move[move] = 1
        else:
            state0 = torch.tensor(state, dtype=torch.float)
            prediction = self.model(state0)
            move = torch.argmax(prediction).item()
            final_move[move] = 1
        return final_move


def train():
    plot_score = []
    plot_mean_score = []
    total_score = 0
    record = 0



    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH,SCREEN_HEIGHT))
    pygame.display.set_caption("PACMAN")
    clock = pygame.time.Clock()
    done = False

    game = Game()
    agent = Agent()
    while True:
        state_old = agent.get_state(game)

        final_move = agent.get_action(state_old)

        done = game.process_events(final_move, human)
        reward, score, done = game.run_logic()

        game.display_frame(screen)

        state_new = agent.get_state(game)

        agent.train_short_memory(state_old, final_move, reward, state_new, done)

        agent.remember(state_old, final_move, reward, state_new, done)

        if done:
            game.reset()
            agent.n_games += 1
            agent.train_long_memory()

            if score > record:
                record = score
                agent.model.save()

            print('Game', agent.n_games, 'Score', score, 'Record', record)

            plot_score.append(score)
            total_score += score
            mean_score = total_score / agent.n_games
            plot_mean_score.append(mean_score)
            plot(plot_score, plot_mean_score)

        clock.tick(30)

    pygame.quit()


if __name__ == '__main__':
    train()
