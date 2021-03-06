import pygame, sys
import random
from modules.constants import *
from modules import utils
from modules.car import Car
from modules.block import Block

# pygame settings
pygame.init()
pygame.mixer.music.load("audio/HandClap.wav")
display = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption('Race Car')
pygame.display.set_icon(pygame.image.load('img/car_icon.png').convert_alpha())

# load image
car1_img = pygame.image.load('img/car1.png').convert_alpha()
car2_img = pygame.image.load('img/car2.png').convert_alpha()
explosion_img = pygame.image.load('img/explosion.png').convert_alpha()
fire_img = pygame.image.load('img/fire.png').convert_alpha()
block1_img = pygame.image.load('img/brick-1.png').convert_alpha()

# Global Variable
crash_sound = pygame.mixer.Sound("audio/Crash.wav")
clock = pygame.time.Clock()
start_time = None
car1 = None
car2 = None
block_list = []
score = 0
level = 1
highest_record = 0


def display_text_label(content, font_size, x_pos, y_pos):
    font = pygame.font.Font("fonts/freesansbold.ttf", font_size)
    text = font.render(content, True, BLACK)
    display.blit(text, (x_pos, y_pos))


def display_block(blocks):
    for b in blocks:
        if not b.crashed:
            display.blit(b.img, (b.x, b.y))
        else:
            display.blit(explosion_img, (b.x, b.y))


def display_car(car):
    display.blit(car.img, (car.x, car.y))


def display_message(msg, font_size, x_pos, y_pos):
    text_style = pygame.font.Font('fonts/freesansbold.ttf', font_size)
    text_surf = text_style.render(msg, True, BLACK)
    text_rect = text_surf.get_rect()
    text_rect.center = (x_pos, y_pos)
    display.blit(text_surf, text_rect)


def display_button(x, y, width, height, text, normal_color, hover_color):
    mouse = pygame.mouse.get_pos()
    click = pygame.mouse.get_pressed()

    if x < mouse[0] < x + width and y < mouse[1] < y + height:
        pygame.draw.rect(display, hover_color, (x, y, width, height))
        if click[0]:
            return 1
    else:
        pygame.draw.rect(display, normal_color, (x, y, width, height))

    text_style = pygame.font.Font('fonts/freesansbold.ttf', 20)
    text_surf = text_style.render(text, True, BLACK)
    text_rect = text_surf.get_rect()
    text_rect.center = (x + width / 2, y + height / 2)
    display.blit(text_surf, text_rect)


def frame_start_menu():
    start_game = False
    btn_width = 100
    btn_height = 50
    start_btn_x = WINDOW_WIDTH / 4
    quit_btn_x = WINDOW_WIDTH - WINDOW_WIDTH / 4 - btn_width
    start_btn_y = quit_btn_y = WINDOW_HEIGHT / 6 * 4

    while not start_game:
        # event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        # display
        display.fill(WHITE)
        display_message("A Racing Car Game", 60, WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2)
        clicked = display_button(start_btn_x, start_btn_y, btn_width, btn_height, "GO!", DARK_GREEN, GREEN)
        if clicked:
            start_game = True
        clicked = display_button(quit_btn_x, quit_btn_y, btn_width, btn_height, "QUIT!", DARK_RED, RED)
        if clicked:
            pygame.quit()
            sys.exit()
        pygame.display.update()

        # FPS
        clock.tick(FPS)


def frame_mode_menu():
    start_game = False
    btn_width = 150
    btn_height = 50
    single_btn_x = WINDOW_WIDTH / 2 - btn_width / 2
    double_btn_x = WINDOW_WIDTH / 2 - btn_width / 2
    single_btn_y = WINDOW_HEIGHT / 6 * 3
    double_btn_y = WINDOW_HEIGHT / 6 * 4

    while not start_game:
        # event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        # display
        display.fill(WHITE)
        display_message("Choose mode", 60, WINDOW_WIDTH / 2, WINDOW_HEIGHT / 3)
        clicked = display_button(single_btn_x, single_btn_y, btn_width, btn_height, "Single Player", DARK_GREEN, GREEN)
        if clicked:
            return SINGLE_MODE
        clicked = display_button(double_btn_x, double_btn_y, btn_width, btn_height, "Double Players", DARK_RED, RED)
        if clicked:
            return DOUBLE_MODE
        pygame.display.update()

        # FPS
        clock.tick(FPS)


def frame_pause():
    paused = True
    btn_width = 100
    btn_height = 50
    pause_btn_x = WINDOW_WIDTH / 4
    quit_btn_x = WINDOW_WIDTH - WINDOW_WIDTH / 4 - btn_width
    pause_btn_y = quit_btn_y = WINDOW_HEIGHT / 6 * 4

    pygame.mixer.music.pause()

    while paused:
        # event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        # display
        clicked = display_button(pause_btn_x, pause_btn_y, btn_width, btn_height, "Continue!", DARK_GREEN, GREEN)
        if clicked:
            paused = False
        clicked = display_button(quit_btn_x, quit_btn_y, btn_width, btn_height, "QUIT!", DARK_RED, RED)
        if clicked:
            pygame.quit()
            sys.exit()

        display_message("Paused!", 100, WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2)
        pygame.display.update()

        # FPS
        clock.tick(FPS)

    pygame.mixer.music.unpause()


def frame_crash(current_time):
    global highest_record, start_time

    crashed = True
    btn_width = 120
    btn_height = 50
    play_btn_x = WINDOW_WIDTH / 4
    quit_btn_x = WINDOW_WIDTH - WINDOW_WIDTH / 4 - btn_width
    play_btn_y = quit_btn_y = WINDOW_HEIGHT / 6 * 4

    # stop bg music, and play crash sound
    pygame.mixer.music.stop()
    pygame.mixer.Sound.play(crash_sound)

    while crashed:
        # event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        # update highest record
        if current_time - start_time > highest_record:
            highest_record = current_time - start_time

        # display
        clicked = display_button(play_btn_x, play_btn_y, btn_width, btn_height, "Play Again!", DARK_GREEN, GREEN)
        if clicked:
            return False
        clicked = display_button(quit_btn_x, quit_btn_y, btn_width, btn_height, "QUIT!", DARK_RED, RED)
        if clicked:
            pygame.quit()
            sys.exit()

        display_message('You Crashed!', 100, WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2)
        pygame.display.update()

        # FPS
        clock.tick(FPS)


def frame_countdown(game_type):
    global car1, car2
    car1_left_key_pressed = car1_right_key_pressed = False
    car2_left_key_pressed = car2_right_key_pressed = False
    start_tick = pygame.time.get_ticks()
    # this list holds display words, one word shows 1s, need '' at the beginning for second element can show for 1s
    countdown_text = ['', 'Game Start!', '1', '2', '3']
    current_display = countdown_text.pop()

    while len(countdown_text) != 0:
        # event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p:
                    frame_pause()
                if event.key == pygame.K_LEFT:
                    car1_left_key_pressed = True
                    car1.x_move = -5
                elif event.key == pygame.K_RIGHT:
                    car1_right_key_pressed = True
                    car1.x_move = 5
                if event.key == pygame.K_a:
                    car2_left_key_pressed = True
                    car2.x_move = -5
                elif event.key == pygame.K_d:
                    car2_right_key_pressed = True
                    car2.x_move = 5

            if event.type == pygame.KEYUP:
                if event.key == pygame.K_RIGHT and car1_left_key_pressed:
                    car1_right_key_pressed = False
                    car1.x_move = -5
                elif event.key == pygame.K_RIGHT:
                    car1_right_key_pressed = False
                    car1.x_move = 0
                if event.key == pygame.K_LEFT and car1_right_key_pressed:
                    car1_left_key_pressed = False
                    car1.x_move = 5
                elif event.key == pygame.K_LEFT:
                    car1_left_key_pressed = False
                    car1.x_move = 0
                if event.key == pygame.K_d and car2_left_key_pressed:
                    car2_right_key_pressed = False
                    car2.x_move = -5
                elif event.key == pygame.K_d:
                    car2_right_key_pressed = False
                    car2.x_move = 0
                if event.key == pygame.K_a and car2_right_key_pressed:
                    car2_left_key_pressed = False
                    car2.x_move = 5
                elif event.key == pygame.K_a:
                    car2_left_key_pressed = False
                    car2.x_move = 0

        # movement variable handling
        # car stops on edge
        if car1.x < 0:
            car1.x_move = 0
            car1.x = 0
        if car1.x > (WINDOW_WIDTH - car1.get_width()):
            car1.x_move = 0
            car1.x = WINDOW_WIDTH - car1.get_width()
        if car2.x < 0:
            car2.x_move = 0
            car2.x = 0
        if car2.x > (WINDOW_WIDTH - car2.get_width()):
            car2.x_move = 0
            car2.x = WINDOW_WIDTH - car2.get_width()
        # stop two cars crossing
        if game_type == DOUBLE_MODE:
            if car2.x + car2.get_width() > car1.x:
                if car1_left_key_pressed and car2_right_key_pressed:
                    car1_stop = car2.x + car2.get_width()
                    car2_stop = car1.x - car2.get_width()
                    car1.x = car1_stop
                    car2.x = car2_stop
                # car1 is pushing car2 to the left
                elif car1_left_key_pressed:
                    car2.x = car1.x - car2.get_width()
                # car2 is pushing car1 to the right
                elif car2_right_key_pressed:
                    car1.x = car2.x + car2.get_width()

        # change movement variable
        car1.change_x()
        car2.change_x()

        # other attribute handling
        # countdown ticker
        current_tick = pygame.time.get_ticks()
        if (current_tick - start_tick) / 1000 > 1:
            start_tick = current_tick
            current_display = countdown_text.pop()

        # display
        display.fill(WHITE)
        display_message(current_display, 100, WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2)
        display_car(car1)
        if game_type == DOUBLE_MODE:
            display_car(car2)
        display_text_label("Record: " + utils.convert_time(highest_record), 25, WINDOW_WIDTH - 240, 0)
        pygame.display.update()

        # FPS
        clock.tick(FPS)

    # set global start timer
    globals()['start_time'] = pygame.time.get_ticks()


def game_init(game_type):
    if game_type == SINGLE_MODE:
        globals()['car1'] = Car(1, car1_img, WINDOW_WIDTH * 0.45, WINDOW_HEIGHT * 0.85)
        globals()['car2'] = Car(2, car2_img, WINDOW_WIDTH * 0.45, WINDOW_HEIGHT * 0.85)
    elif game_type == DOUBLE_MODE:
        globals()['car1'] = Car(1, car1_img, WINDOW_WIDTH * 0.75, WINDOW_HEIGHT * 0.85)
        globals()['car2'] = Car(2, car2_img, WINDOW_WIDTH * 0.25, WINDOW_HEIGHT * 0.85)
    globals()['block_list'].clear()
    globals()['block_list'].append(Block(block1_img,
                                         random.randint(0, WINDOW_WIDTH), -WINDOW_HEIGHT, 5))
    globals()['block_list'].append(Block(block1_img,
                                         random.randint(0, WINDOW_WIDTH), -WINDOW_HEIGHT, 5))
    globals()['block_list'].append(Block(block1_img,
                                         random.randint(0, WINDOW_WIDTH), -WINDOW_HEIGHT, 5))
    globals()['score'] = 0
    globals()['level'] = 1

    frame_countdown(game_type)
    pygame.mixer.music.play(-1)


def check_crash(car, blocks):
    """method checks if one car crashes on one block"""

    for b in blocks:
        if utils.crash_detection(car, b) and not b.crashed:
            b.crashed = True
            return True
    return False


def check_two_cars_crash(car1, car2, blocks):
    """method checks if two cars crash on the same block at the same time"""

    for b in blocks:
        if utils.crash_detection(car1, b) and utils.crash_detection(car2, b) and not b.crashed:
            b.crashed = True
            return True
    return False


def single_game_loop():
    global score, level, car1, block_list
    # key lock
    left_key_pressed = False
    right_key_pressed = False
    game_exit = False

    while not game_exit:
        level_up = False
        # event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                # left right key
                if event.key == pygame.K_LEFT:
                    left_key_pressed = True
                    car1.x_move = -5
                elif event.key == pygame.K_RIGHT:
                    right_key_pressed = True
                    car1.x_move = 5
                elif event.key == pygame.K_p:
                    frame_pause()
                # up down key
                if event.key == pygame.K_UP:
                    car1.y_move = -5
                elif event.key == pygame.K_DOWN:
                    car1.y_move = 5

            if event.type == pygame.KEYUP:
                # left right key
                if event.key == pygame.K_RIGHT and left_key_pressed:
                    right_key_pressed = False
                    car1.x_move = -5
                elif event.key == pygame.K_RIGHT:
                    right_key_pressed = False
                    car1.x_move = 0
                if event.key == pygame.K_LEFT and right_key_pressed:
                    left_key_pressed = False
                    car1.x_move = 5
                elif event.key == pygame.K_LEFT:
                    left_key_pressed = False
                    car1.x_move = 0
                # up down key
                if event.key == pygame.K_UP or event.key == pygame.K_DOWN:
                    car1.y_move = 0

        # movement variable handling
        # car stops on edge
        if car1.x < 0:
            car1.x_move = 0
            car1.x = 0
        if car1.x > (WINDOW_WIDTH - car1.get_width()):
            car1.x_move = 0
            car1.x = WINDOW_WIDTH - car1.get_width()
        if car1.y < 0:
            car1.y_move = 0
            car1.y = 0
        if car1.y > (WINDOW_HEIGHT - car1.get_height()):
            car1.y_move = 0
            car1.y = WINDOW_HEIGHT - car1.get_height()
        # block passes bottom, initialize block position
        for b in block_list:
            if b.y > WINDOW_HEIGHT:
                b.set_to_top()
                score += 1
                level = utils.calculate_level(score)
                level_up = utils.level_up(score)

        # change movement variable
        car1.change_x()
        car1.change_y()
        for b in block_list:
            b.change_y()

        # other attributes handling
        # car crashes on blocks
        if check_crash(car1, block_list):
            car1.life = car1.life - 1
            pygame.mixer.Sound.play(crash_sound)
            if car1.life < 0:
                return current_time
        # level up change
        if level_up:
            for b in block_list:
                b.speed = utils.calculate_speed(b.speed, level)
        # capture time
        current_time = pygame.time.get_ticks()

        # display
        display.fill(WHITE)
        display_car(car1)
        display_block(block_list)
        display_text_label("Time: " + utils.convert_time(current_time - start_time), 25, 0, 0)
        display_text_label("Level: " + str(level), 25, 0, 30)
        display_text_label("Life: " + str(car1.life), 25, 0, 60)
        display_text_label("Record: " + utils.convert_time(highest_record), 25, WINDOW_WIDTH - 240, 0)
        pygame.display.update()

        # FPS
        clock.tick(FPS)


def double_game_loop():
    global score, level, car1, car2, block_list
    car1.restore()
    car2.restore()
    # key lock
    car1_left_key_pressed = False
    car1_right_key_pressed = False
    car2_left_key_pressed = False
    car2_right_key_pressed = False
    # display lock
    display_car1 = True
    display_car2 = True
    game_exit = False

    while not game_exit:
        level_up = False
        display_fire = False
        # event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p:
                    frame_pause()
                if display_car1:
                    if event.key == pygame.K_LEFT:
                        car1_left_key_pressed = True
                        car1.x_move = -5
                    elif event.key == pygame.K_RIGHT:
                        car1_right_key_pressed = True
                        car1.x_move = 5
                    # up down key
                    if event.key == pygame.K_UP:
                        car1.y_move = -5
                    elif event.key == pygame.K_DOWN:
                        car1.y_move = 5
                if display_car2:
                    if event.key == pygame.K_a and display_car2:
                        car2_left_key_pressed = True
                        car2.x_move = -5
                    elif event.key == pygame.K_d and display_car2:
                        car2_right_key_pressed = True
                        car2.x_move = 5
                    # w s key
                    if event.key == pygame.K_w:
                        car2.y_move = -5
                    elif event.key == pygame.K_s:
                        car2.y_move = 5
            if event.type == pygame.KEYUP:
                if display_car1:
                    if event.key == pygame.K_RIGHT and car1_left_key_pressed:
                        car1_right_key_pressed = False
                        car1.x_move = -5
                    elif event.key == pygame.K_RIGHT and display_car1:
                        car1_right_key_pressed = False
                        car1.x_move = 0
                    if event.key == pygame.K_LEFT and car1_right_key_pressed:
                        car1_left_key_pressed = False
                        car1.x_move = 5
                    elif event.key == pygame.K_LEFT:
                        car1_left_key_pressed = False
                        car1.x_move = 0
                    # up down key
                    if event.key == pygame.K_UP or event.key == pygame.K_DOWN:
                        car1.y_move = 0
                if display_car2:
                    if event.key == pygame.K_d and car2_left_key_pressed:
                        car2_right_key_pressed = False
                        car2.x_move = -5
                    elif event.key == pygame.K_d:
                        car2_right_key_pressed = False
                        car2.x_move = 0
                    if event.key == pygame.K_a and car2_right_key_pressed:
                        car2_left_key_pressed = False
                        car2.x_move = 5
                    elif event.key == pygame.K_a:
                        car2_left_key_pressed = False
                        car2.x_move = 0
                    # w s key
                    if event.key == pygame.K_w or event.key == pygame.K_s:
                        car2.y_move = 0
        # movement variable handling
        # car stops on edge
        if car1.x < 0:
            car1.x_move = 0
            car1.x = 0
        if car1.x > (WINDOW_WIDTH - car1.get_width()):
            car1.x_move = 0
            car1.x = WINDOW_WIDTH - car1.get_width()
        if car1.y < 0:
            car1.y_move = 0
            car1.y = 0
        if car1.y > (WINDOW_HEIGHT - car1.get_height()):
            car1.y_move = 0
            car1.y = WINDOW_HEIGHT - car1.get_height()
        if car2.x < 0:
            car2.x_move = 0
            car2.x = 0
        if car2.x > (WINDOW_WIDTH - car2.get_width()):
            car2.x_move = 0
            car2.x = WINDOW_WIDTH - car2.get_width()
        if car2.y < 0:
            car2.y_move = 0
            car2.y = 0
        if car2.y > (WINDOW_HEIGHT - car2.get_height()):
            car2.y_move = 0
            car2.y = WINDOW_HEIGHT - car2.get_height()
        # stop two cars crossing
        # if car2.x + car2.get_width() > car1.x:
        #     if car1_left_key_pressed and car2_right_key_pressed and display_car1 and display_car2:
        #         car1_stop = car2.x + car2.get_width()
        #         car2_stop = car1.x - car2.get_width()
        #         car1.x = car1_stop
        #         car2.x = car2_stop
        #         display_fire = True
        #     # car1 is pushing car2 to the left
        #     elif car1_left_key_pressed and display_car1:
        #         car2.x = car1.x - car2.get_width()
        #     # car2 is pushing car1 to the right
        #     elif car2_right_key_pressed and display_car2:
        #         car1.x = car2.x + car2.get_width()

        # change movement variable
        car1.change_x()
        car1.change_y()
        car2.change_x()
        car2.change_y()
        for b in block_list:
            b.change_y()

        # car crashes on blocks
        if display_car1 and display_car2 and check_two_cars_crash(car1, car2, block_list):
            pygame.mixer.Sound.play(crash_sound)
            car1.life = car1.life - 1
            car2.life = car2.life - 1
        elif display_car1 and check_crash(car1, block_list):
            pygame.mixer.Sound.play(crash_sound)
            car1.life = car1.life - 1
        elif display_car2 and check_crash(car2, block_list):
            pygame.mixer.Sound.play(crash_sound)
            car2.life = car2.life - 1
        if car1.life < 0:
            display_car1 = False
        if car2.life < 0:
            display_car2 = False
        if not display_car1 and not display_car2:
            return current_time
        # block passes window, initialize block position
        for b in block_list:
            if b.y > WINDOW_HEIGHT:
                b.set_to_top()
                score += 1
                level = utils.calculate_level(score)
                level_up = utils.level_up(score)
        # level up change
        if level_up:
            for b in block_list:
                b.speed = utils.calculate_speed(b.speed, level)
        # capture time
        current_time = pygame.time.get_ticks()

        # display
        display.fill(WHITE)
        if display_car1:
            display_car(car1)
            display_text_label("Life: " + str(car1.life), 25, WINDOW_WIDTH - 240, 60)
        else:
            display_text_label("Life: 0", 25, WINDOW_WIDTH - 240, 60)

        if display_car2:
            display_car(car2)
            display_text_label("Life: " + str(car2.life), 25, 0, 60)
        else:
            display_text_label("Life: 0", 25, 0, 60)

        # if display_fire:
        #     display.blit(fire_img, (car1_stop - fire_img.get_rect().width / 2, WINDOW_HEIGHT * 0.85))
        display_block(block_list)
        display_text_label("Time: " + utils.convert_time(current_time - start_time), 25, 0, 0)
        display_text_label("Level: " + str(level), 25, WINDOW_WIDTH / 2, 0)
        display_text_label("Record: " + utils.convert_time(highest_record), 25, WINDOW_WIDTH - 240, 0)
        pygame.display.update()

        # FPS
        clock.tick(FPS)


if __name__ == "__main__":
    game_continue = True
    game_type = SINGLE_MODE
    frame_start_menu()

    while game_continue:
        game_type = frame_mode_menu()
        if game_type == SINGLE_MODE:
            game_init(game_type)
            current_time = single_game_loop()
            if frame_crash(current_time):
                game_continue = False
        elif game_type == DOUBLE_MODE:
            game_init(game_type)
            current_time = double_game_loop()
            if frame_crash(current_time):
                game_continue = False

    pygame.quit()
    sys.exit()
