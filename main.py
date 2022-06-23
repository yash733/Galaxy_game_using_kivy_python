import random

from kivy.config import Config
from kivy.core.audio import SoundLoader
from kivy.lang import Builder
from kivy.uix.relativelayout import RelativeLayout

Config.set('graphics', 'width', '900')
Config.set('graphics', 'height', '400')

from kivy import platform
from kivy.core.window import Window
from kivy.app import App
from kivy.graphics.context_instructions import Color
from kivy.graphics.vertex_instructions import Line, Quad, Triangle, Ellipse
from kivy.properties import NumericProperty, Clock, ObjectProperty, StringProperty
from kivy.uix.widget import Widget

Builder.load_file("menu.kv")

class MainWidget(RelativeLayout):
    menu_widget = ObjectProperty()
    perspective_point_x = NumericProperty(0)
    perspective_point_y = NumericProperty(0)

    V_NB_LINES = 8
    V_LINES_SPACING = .3  # percentage in screen width
    vertical_lines = []

    H_NB_LINES = 15
    H_LINES_SPACING = .2  # percentage in screen height
    horizontal_lines = []

    SPEED = .8
    speed = SPEED
    current_offset_y = 0
    current_y_loop = 0

    SPEED_X = 3.0
    speed_x = SPEED_X
    current_speed_x = 0
    current_offset_x = 0

    NB_TILES = 16
    tiles = []
    tiles_coordinates = []

    SHIP_WIDTH = .14
    SHIP_HEIGHT = 0.028
    SHIP_BASE_Y = 0.03
    ship = None
    ship_coordinates = [(0, 0), (0, 0), (0, 0)]

    game_over = False
    game_started = False

    menu_title = StringProperty("G   A   L   A   X   Y")
    menu_button_title = StringProperty("START")

    score_txt = StringProperty()
    highscore_txt = StringProperty()
    highscore = 0

    #sound_begin = None
    sound_galaxy = None
    sound_gameover_impact = None
    sound_gameover_voice = None
    sound_music1 = None
    sound_restart = None

    # check_highscore
    i = 0

    def __init__(self, **kwargs):
        super(MainWidget, self).__init__(**kwargs)
        # print("INIT W:" + str(self.width) + " H:" + str(self.height))
        self.init_audio()
        self.init_vertical_lines()
        self.init_horizontal_lines()
        self.init_tiles()
        # self.init_ship_shadow()
        self.init_ship()
        self.reset_game()

        if self.is_desktop():
            self._keyboard = Window.request_keyboard(self.keyboard_close, self)
            self._keyboard.bind(on_key_down=self.on_keyboard_down)
            self._keyboard.bind(on_key_up=self.on_keyboard_up)

        Clock.schedule_interval(self.update, 1.0 / 60.0)


    sound_begin = SoundLoader.load("audio/begin.wav")
    sound_galaxy = SoundLoader.load("audio/galaxy.wav")
    sound_galaxy.play()
    sound_highscore = SoundLoader.load("audio/highscore.wav")

    sound_gameover_impact = SoundLoader.load("audio/game-over-arcade-6435.wav")
    sound_gameover_voice = SoundLoader.load("audio/gameover_voice.wav")
    sound_music1 = SoundLoader.load("audio/game_music.wav")
    sound_restart = SoundLoader.load("audio/restart.wav")
    sound_ingame = SoundLoader.load("audio/game_in.wav")

    def init_audio(self):

        self.sound_music1.volume = 1
        self.sound_begin.volume = .25
        self.sound_galaxy.volume = .25
        self.sound_gameover_voice.volume = .25
        self.sound_restart.volume = .25
        self.sound_gameover_impact.volume = 1
        self.sound_highscore.volume = 1
        self.sound_ingame.volume = 1


    def reset_game(self):
        self.current_offset_y = 0
        self.current_y_loop = 0
        self.tiles_coordinates = []
        self.current_speed_x = 0
        self.current_offset_x = 0
        self.score_txt = "SCORE : " + str(self.current_y_loop)
        self.highscore_txt = "HIGH SCORE : " + str(self.highscore)
        self.SPEED = 0.8

        self.pre_fill_tiles_coordinate()
        self.generate_tiles_coordinates()
        self.game_over = False
        self.game_started = False
        self.j = 0


    def keyboard_close(self):
        self._keyboard.unbind(on_key_down=self.on_keyboard_down)
        self._keyboard.unbind(on_key_up=self.on_keyboard_up)
        self._keyboard = None

    def is_desktop(self):
        if platform in ('linux', 'win', 'macosx'):
            return True
        return False

    '''def init_ship_shadow(self):
        with self.canvas:
            Color(0, 1, 1)
            self.ship_s = Triangle()'''

    def init_ship(self):
        with self.canvas:
            Color(0, 0, 0)
            self.ship = Triangle()

    def update_ship(self):
        center_x = self.width / 2
        base_y = self.SHIP_BASE_Y * self.height
        ship_half_width = self.SHIP_WIDTH * self.width / 2
        ship_height = self.SHIP_HEIGHT * self.height

        # ---------
        # --- 2 ---
        # -- --- --
        # 1 ----- 3

        self.ship_coordinates[0] = (center_x - ship_half_width, base_y)
        self.ship_coordinates[1] = (center_x, base_y + ship_height)
        self.ship_coordinates[2] = (center_x + ship_half_width, base_y)

        x1, y1 = self.transform(*self.ship_coordinates[0])
        x2, y2 = self.transform(*self.ship_coordinates[1])
        x3, y3 = self.transform(*self.ship_coordinates[2])

        self.ship.points = [x1, y1, x2, y2, x3, y3]

    def check_ship_collision(self):
        for i in range(0, len(self.tiles_coordinates)):
            ti_x, ti_y = self.tiles_coordinates[i]
            if ti_y > self.current_y_loop + 1:
                return False
            if self.check_ship_collision_with_tile(ti_x, ti_y):
                return True
        return False

    def check_ship_collision_with_tile(self, ti_x, ti_y):
        x_min, y_min = self.get_tile_coordinates(ti_x, ti_y)
        x_max, y_max = self.get_tile_coordinates(ti_x + 1, ti_y + 1)
        for i in range(0, 3):
            px, py = self.ship_coordinates[i]
            if x_min <= px <= x_max and y_min <= py <= y_max:
                return True
        return False

        # Checking if ship is on the track
        '''
        if x_min <= ship_points_x[0] <= x_max and y_min <= ship_points_y[0] <= y_max:
            if x_min <= ship_points_x[1] <= x_max and y_min <= ship_points_y[1] <= y_max:
                if x_min <= ship_points_x[2] <= x_max and y_min <= ship_points_y[2] <= y_max:
                    # print("True")
                    return True        # print("false")
        ''''''s = 0
        for i in range(0, 3):
            if x_min <= ship_points_x[i] <= x_max and y_min <= ship_points_y[i] <= y_max:
                s += 1
                if s == 3:
                    return True '''

    def init_tiles(self):
        with self.canvas:
            Color(.5, 1, 1, .4)
            for i in range(0, self.NB_TILES):
                self.tiles.append(Quad())

    def pre_fill_tiles_coordinate(self):
        l = random.randint(5, 10)
        # also use random function
        # for i in range(0, l):
        for i in range(0, l):
            self.tiles_coordinates.append((0, i))

    def generate_tiles_coordinates(self):
        last_x = 0
        last_y = 0

        # clean the coordinates that are out of the screen
        # ti_y < self.current_y_loop
        for i in range(len(self.tiles_coordinates) - 1, -1, -1):
            if self.tiles_coordinates[i][1] < self.current_y_loop:
                del self.tiles_coordinates[i]

        if len(self.tiles_coordinates) > 0:
            last_coordinates = self.tiles_coordinates[-1]
            last_x = last_coordinates[0]
            last_y = last_coordinates[1] + 1

        for i in range(len(self.tiles_coordinates), self.NB_TILES):
            r = random.randint(0, 2)
            # 0 -> straight
            # 1 -> right
            # 2 -> left
            start_index = -int(self.V_NB_LINES / 2) + 1
            end_index = start_index + self.V_NB_LINES - 2
            if last_x <= start_index:
                r = 1
            if last_x >= end_index:
                r = 2

            self.tiles_coordinates.append((last_x, last_y))
            if r == 1:
                last_x += 1
                self.tiles_coordinates.append((last_x, last_y))
                last_y += 1
                self.tiles_coordinates.append((last_x, last_y))
            if r == 2:
                last_x -= 1
                self.tiles_coordinates.append((last_x, last_y))
                last_y += 1
                self.tiles_coordinates.append((last_x, last_y))

            last_y += 1

    def init_vertical_lines(self):
        with self.canvas:
            Color(1, 1, 1, 0.1)
            # self.line = Line(points=[100, 0, 100, 100])
            for i in range(0, self.V_NB_LINES):
                self.vertical_lines.append(Line())


    def get_line_x_from_index(self, index):
        central_line_x = self.perspective_point_x
        spacing = self.V_LINES_SPACING * self.width
        offset = index - 0.5
        line_x = central_line_x + offset * spacing + self.current_offset_x
        return line_x

    def get_line_y_from_index(self, index):
        spacing_y = self.H_LINES_SPACING * self.height
        line_y = index * spacing_y - self.current_offset_y
        return line_y

    def get_tile_coordinates(self, ti_x, ti_y):
        ti_y = ti_y - self.current_y_loop
        x = self.get_line_x_from_index(ti_x)
        y = self.get_line_y_from_index(ti_y)
        return x, y

    def update_tiles(self):
        for i in range(0, self.NB_TILES):
            tile = self.tiles[i]
            tile_coordinates = self.tiles_coordinates[i]
            x_min, y_min = self.get_tile_coordinates(tile_coordinates[0], tile_coordinates[1])
            x_max, y_max = self.get_tile_coordinates(tile_coordinates[0] + 1, tile_coordinates[1] + 1)

            #  2    3
            #
            #  1    4
            x1, y1 = self.transform(x_min, y_min)
            x2, y2 = self.transform(x_min, y_max)
            x3, y3 = self.transform(x_max, y_max)
            x4, y4 = self.transform(x_max, y_min)

            tile.points = [x1, y1, x2, y2, x3, y3, x4, y4]

    def update_vertical_lines(self):
        # -1 0 1 2
        ''' central_line_x = int(self.width / 2)
                spacing = self.V_LINES_SPACING * self.width
                offset = -int(self.V_NB_LINES/2)+0.5 '''
        start_index = -int(self.V_NB_LINES / 2) + 1
        for i in range(start_index, start_index + self.V_NB_LINES):
            line_x = self.get_line_x_from_index(i)

            x1, y1 = self.transform(line_x, 0)
            x2, y2 = self.transform(line_x, self.height)
            self.vertical_lines[i].points = [x1, y1, x2, y2]

    def init_horizontal_lines(self):
        with self.canvas:
            Color(1, 1, 1, 0.1)
            for i in range(0, self.H_NB_LINES):
                self.horizontal_lines.append(Line())


    def update_horizontal_lines(self):
        ''' central_line_x = int(self.width / 2)
        spacing = self.V_LINES_SPACING * self.width
        offset = int(self.V_NB_LINES / 2) - 0.5 '''

        start_index = -int(self.V_NB_LINES / 2) + 1
        end_index = start_index + self.V_NB_LINES - 1

        x_min = self.get_line_x_from_index(start_index)
        x_max = self.get_line_x_from_index(end_index)
        for i in range(0, self.H_NB_LINES):
            line_y = self.get_line_y_from_index(i)
            x1, y1 = self.transform(x_min, line_y)
            x2, y2 = self.transform(x_max, line_y)
            self.horizontal_lines[i].points = [x1, y1, x2, y2]

    def transform(self, x, y):
        # return self.transform_2D(x, y)
        return self.transform_perspective(x, y)

    def transform_2D(self, x, y):
        return int(x), int(y)

    def transform_perspective(self, x, y):
        lin_y = y * self.perspective_point_y / self.height
        if lin_y > self.perspective_point_y:
            lin_y = self.perspective_point_y

        diff_x = x - self.perspective_point_x
        diff_y = self.perspective_point_y - lin_y
        factor_y = diff_y / self.perspective_point_y  # 1 when diff_y == self.perspective_point_y / 0 when diff_y = 0
        factor_y = pow(factor_y, 4)

        tr_x = self.perspective_point_x + diff_x * factor_y - 14
        tr_y = self.perspective_point_y - factor_y * self.perspective_point_y + 5

        return int(tr_x), int(tr_y)

    def on_keyboard_down(self, keyboard, keycode, text, modifiers):
        if keycode[1] == 'left':
            self.current_speed_x = self.SPEED_X
        if keycode[1] == 'a':
            self.current_speed_x = self.SPEED_X

        if keycode[1] == 'right':
            self.current_speed_x = - self.SPEED_X
        if keycode[1] == 'd':
            self.current_speed_x = - self.SPEED_X

        if keycode[1] == 'w':
            self.SPEED += 0.3
            self.SPEED_X += 0.1
        if keycode[1] == 'up':
            self.SPEED += 0.3
            self.SPEED_X += 0.1

        if keycode[1] == 's':
            if self.speed < self.SPEED:
                self.SPEED -= 0.3
                if self.speed_x < self.SPEED_X:
                    self.SPEED_X -=0.01
        if keycode[1] == 'down':
            if self.speed < self.SPEED:
                self.SPEED -= 0.3
                if self.speed_x < self.SPEED_X:
                    self.SPEED_X -= 0.01
        return True

    def on_keyboard_up(self, keyboard, keycode):
        self.current_speed_x = 0
        return True

    def on_touch_down(self, touch):
        if self.game_over == False and self.game_started == True:
            if touch.x < self.width / 2:
                # print("<-")
                self.current_speed_x = self.SPEED_X
            else:
                # print("->")
                self.current_speed_x = -self.SPEED_X
            # return self.on_touch_down(touch)
        ''' if self.game_over == True:
            return self.menu_button()'''

        return self.menu_button()

    def on_touch_up(self, touch):
        # print("UP")
        self.current_speed_x = 0

    def update(self, dt):
        # print("dt: " + str(dt*60))
        time_factor = dt * 60
        self.update_vertical_lines()
        self.update_horizontal_lines()
        self.update_tiles()
        self.update_ship()
        self.ckeck_score()

        if not self.game_over and self.game_started:
            speed_y = self.SPEED * self.height / 100
            self.current_offset_y += speed_y * time_factor

            spacing_y = self.H_LINES_SPACING * self.height
            while self.current_offset_y >= spacing_y:
                self.current_offset_y -= spacing_y
                self.current_y_loop += 1
                self.score_txt = "SCORE : " + str(self.current_y_loop)

                self.SPEED += .000009
                if self.SPEED >= 9:
                    self.SPEED = 8

                self.generate_tiles_coordinates()

            speed_x = self.current_speed_x * self.height / 100
            self.current_offset_x += speed_x * time_factor


        # when check_ship_collision == True ---> means ship on track
        if self.check_ship_collision() == False and self.game_over == False:
            self.game_over = True
            self.menu_title = "G A M E  O V E R"
            self.menu_button_title = "PLAY AGAIN"
            self.sound_music1.stop()
            print("Game Over")
            Clock.schedule_once(self.game_over_voice, 5)
            self.sound_gameover_impact.play()
            self.menu_widget.opacity = 1

            if self.i < 1:
                self.highscore = self.current_y_loop
                print(f"Highscore after 1st {self.highscore}")
                self.i += 1

    def game_over_voice(self, dt):
        if self.game_over:
            self.sound_gameover_voice.play()

        # Storing 1st highscore ...
    def ckeck_score(self):
        if self.i >= 1 and self.highscore < self.current_y_loop:
            self.highscore = self.current_y_loop
            print(f"new highscore {self.highscore}")
            if self.j == 0:
                self.sound_highscore.play()
                self.j += 1
                print("Sound on ")


    def menu_button(self, touch=None):
        if self.game_over == False and self.game_started == False:
            print("BUTTON")
            self.game_started = True
            self.sound_music1.play()
            self.sound_music1.loop = True
            self.menu_widget.opacity = 0
            self.sound_begin.play()

        # Game Restart  --->
        if self.game_over == True:
            self.sound_restart.play()
            self.reset_game()
            print("Restart Button")
            self.sound_ingame.play()
            self.sound_music1.play()
            self.game_started = True
            self.menu_widget.opacity = 0


class GalaxyApp(App):
    pass


GalaxyApp().run()
