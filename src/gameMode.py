"""
This is a base class for different mode in game.
"""
from .car import Car
from .points import *
from .maze_wall import SlantWall

import pygame

from .env import *


class GameMode(object):
    def __init__(self, bg_img=pygame.Surface((WIDTH, HEIGHT))):
        self.bg_img = bg_img
        self.clock = pygame.time.Clock()
        self.running = True
        self.frame = 0
        pygame.font.init()
        self.font = pygame.font.Font(pygame.font.match_font("arial", bold=True), 15)
        self.time_font = pygame.font.Font(pygame.font.match_font("arial", bold=True), 46)
        self.check_point_num = 0
        self.check_points = []
        # self.start_time = time.time()

    def ticks(self, fps=FPS):
        """This method should be called once per frame.
        It will compute how many milliseconds have passed since the previous call.
        :param fps: frame per second 每秒的繪圖次數
        :return: None
        """
        self.clock.tick(fps)

    def handle_event(self):
        """ Handle the event from window , mouse or button.
        :return: None
        """
        pass

    def detect_collision(self):
        """ Detect the collision event between sprites.
        :return: None
        """
        pass

    def update_sprite(self, *args):
        """ This function should update every sprite in games.
        :return: None
        """
        pass

    def draw_bg(self):
        """  Draw a background on screen.
        :return:None
        """
        pass

    def drawWorld(self):
        """  This function should draw every sprite on specific surface.
        :return: None
        """
        pass

    def flip(self):
        """Update the full display Surface to the screen
        :return:None
        """
        pygame.display.flip()

    def isRunning(self) -> bool:
        return self.running

    def rank(self):
        '''
        不限碰撞次數，但須在規定時間內過關
        排名依據：
        1. 檢查點個數（走到終點及取得所有檢查點）。
        2. 若檢查點個數相同，則比較碰撞次數，越少者排名越前。
        3. 碰撞次數相同，則比較走到最末檢查點的時間，越早走到者排名越前。
        '''
        user_check_point = []
        user_crush_times = []
        user_end_frame = []
        user_score = []
        for car in self.eliminated_user:
            user_check_point.append(car.check_point)
            user_crush_times.append(car.collide_times)
            user_end_frame.append(car.end_frame)
            user_score.append(car.check_point * 10000 - car.collide_times * 10 - car.end_frame * 0.001)
        rank_user = []  # [sprite]

        result = [user_score.index(x) for x in sorted(user_score, reverse=True)]
        for i in range(len(result)):
            rank_user.append(self.eliminated_user[result[i]])
        return rank_user

    def trnsfer_box2d_to_pygame(self, coordinate):
        '''
        :param coordinate: vertice of body of box2d object
        :return: center of pygame rect
        '''
        return ((coordinate[0] - self.pygame_point[0]) * PPM, (self.pygame_point[1] - coordinate[1]) * PPM)

    def get_wall_info_v(self, wall_tile):
        wall_tiles = []
        for col in range(len(self.map.data[0]) - 1):
            row = 0
            first_tile = -1
            last_tile = -1
            while row < len(self.map.data):
                tiles = self.map.data[row]

                if (tiles[col] % 18) == wall_tile:
                    if first_tile == -1:
                        first_tile = row
                        if row == len(self.map.data) - 1:
                            last_tile = row
                            self.wall_vertices_for_Box2D.append(
                                {"type": wall_tile,
                                 "vertices": self.wall_vertices_v((col, first_tile), (col, last_tile))})
                            first_tile = -1
                            row += 1
                        else:
                            row += 1
                    elif row == len(self.map.data) - 1:
                        last_tile = row
                        self.wall_vertices_for_Box2D.append(
                            {"type": wall_tile, "vertices": self.wall_vertices_v((col, first_tile), (col, last_tile))})
                        first_tile = -1
                        row += 1
                    else:
                        row += 1
                else:
                    if first_tile != -1:
                        last_tile = row - 1
                        self.wall_vertices_for_Box2D.append(
                            {"type": wall_tile, "vertices": self.wall_vertices_v((col, first_tile), (col, last_tile))})
                        # self.wall_vertices_for_Box2D.append(self.wall_vertices_v((col, first_tile), (col, last_tile)))
                        first_tile = -1
                        row += 1
                    else:
                        row += 1

    def get_wall_info_h(self, wall_tile):
        wall_tiles = []
        for row, tiles in enumerate(self.map.data):
            col = 0
            first_tile = -1
            last_tile = -1
            while col < (len(tiles)):
                if (tiles[col] % 18) == wall_tile:
                    if first_tile == -1:
                        first_tile = col
                        if col == len(tiles) - 1:
                            first_tile = -1
                            col += 1
                        else:
                            col += 1
                    elif col == len(tiles) - 1:
                        last_tile = col
                        self.wall_vertices_for_Box2D.append(
                            {"type": wall_tile, "vertices": self.wall_vertices_h((first_tile, row), (last_tile, row))})
                        # self.wall_vertices_for_Box2D.append(self.wall_vertices_h((first_tile, row), (last_tile, row)))
                        for i in range(first_tile, last_tile + 1):
                            tiles[i] = 0
                        first_tile = -1
                        col += 1
                    else:
                        col += 1
                else:
                    if first_tile != -1:
                        last_tile = col - 1
                        if first_tile == last_tile:
                            first_tile = -1
                            col += 1
                        else:
                            self.wall_vertices_for_Box2D.append(
                                {"type": wall_tile,
                                 "vertices": self.wall_vertices_h((first_tile, row), (last_tile, row))})
                            for i in range(first_tile, last_tile + 1):
                                tiles[i] = 0
                            first_tile = -1
                            col += 1
                    else:
                        col += 1

    def _print_result(self):
        if self.is_end and self.x == 0:
            for user in self.ranked_user:
                self.result.append(str(user.car_no + 1) + "P:" + str(user.end_frame) + "frame")
            self.x += 1
            print(self.result)

    def load_map_object(self, obj):
        o = obj["end_point"]
        self.end_point = End_point(self, (o[1], o[0]))
        self.check_point_num += 1
        o = obj["check_point"]
        for p in o:
            check_point = Check_point(self, (p[1], p[0]))
            self.check_point_num += 1
            self.check_points.append(check_point.get_info()["coordinate"])
        o = obj["car"]
        if o[2] == 6 or o[2] == 10:
            for world in self.worlds:
                car = Car(world, (o[1], o[0]), self.worlds.index(world), self.sensor_num, 2)
                self.cars.add(car)
                self.car_info.append(car.get_info())
        elif o[2] == 13:
            for world in self.worlds:
                car = Car(world, (o[1], o[0]), self.worlds.index(world), self.sensor_num, 0.5)
                self.cars.add(car)
                self.car_info.append(car.get_info())
        elif o[2] == 12:
            for world in self.worlds:
                car = Car(world, (o[1], o[0]), self.worlds.index(world), self.sensor_num, 1)
                self.cars.add(car)
                self.car_info.append(car.get_info())
        elif o[2] == 11:
            for world in self.worlds:
                car = Car(world, (o[1], o[0]), self.worlds.index(world), self.sensor_num, 1.5)
                self.cars.add(car)
                self.car_info.append(car.get_info())
        try:
            if self.end_point and len(self.cars):
                pass
            else:
                print("Map without car")
                self.running = False
        except:
            print("Map without end point")
            self.running = False
