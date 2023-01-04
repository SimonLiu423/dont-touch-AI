import pygame
import Box2D
from os import path
from mlgame.game.paia_game import GameResultState, GameStatus
from mlgame.utils.enum import get_ai_name
from mlgame.view.view_model import create_line_view_data, create_polygon_view_data, create_rect_view_data, \
    create_asset_init_data, create_image_view_data, create_text_view_data
from .tiledMap_to_box2d import TiledMap_box2d
from .maze_wall import Wall
from .car import Car
from .points import End_point

# from game_module.TiledMap import create_construction
from .env import *


class SingleMode:
    def __init__(self):
        pygame.init()
        self._user_num = 1
        # self.play_rect_area = play_rect_area # 這個的作用是啥
        self.all_sprites = pygame.sprite.Group()
        self.used_frame = 0
        self.state = GameResultState.FAIL
        self.status = GameStatus.GAME_ALIVE
        self.width_center = WIDTH // 2
        self.height_center = HEIGHT // 2
        self.obj_rect_list = []
        self.walls = pygame.sprite.Group()
        self.walls_info = []
        self.init_world()

    def update(self, command: dict) -> None:
        self.used_frame += 1
        # self.car.update({"left_PWM": 100, "right_PWM": 100})
        self.car.update(command["1P"])
        self.car.rect.center = self.car.body.position[0] * PPM, self.car.body.position[1] * PPM
        # print(self.car.get_info())
        # self.car.detect_distance(self.used_frame, self.walls)
        if self.used_frame > 600:
            self.get_player_end()

    def reset(self) -> None:
        pass

    def get_player_end(self):
        self.set_result(GameResultState.FINISH, GameStatus.GAME_OVER)

    def set_result(self, state: str, status: str):
        self.state = state
        self.status = status

    def get_player_result(self) -> list:
        """Define the end of game will return the player's info for user"""
        res = []
        # get_res["state"] = self.state
        # get_res["status"] = self.status
        # get_res["used_frame"] = self.used_frame
        # res.append(get_res)
        return res

    def get_init_image_data(self):
        init_image_data = []
        file_path = path.join(IMAGE_DIR, "car_01.png")
        init_image_data.append(create_asset_init_data("car", 50, 50, file_path, "test"))
        file_path = path.join(IMAGE_DIR, "heart.png")
        init_image_data.append(create_asset_init_data("life", 30, 30, file_path, "test"))
        return init_image_data

    def get_ai_data_to_player(self):
        to_player_data = {"id": "1P", "x": 50, "y": 50, "angle": 3, "used_frame": self.used_frame,
                          "status": self.status}

        return {get_ai_name(0): to_player_data}

    def get_obj_progress_data(self) -> list:
        obj_progress_data = []
        # 寫入view資訊
        self.obj_rect_list.extend(self.walls_info)
        car_info = self.car.get_info()
        self.obj_rect_list.append(create_image_view_data("car", car_info["topleft"][0], car_info["topleft"][1], 50, 40,
                                       car_info["angle"]))
        self.obj_rect_list.append(create_text_view_data("{0:05d} frames".format(self.used_frame), 810, 60, WHITE, font_style="28px Arial"))
        self.obj_rect_list.append(create_image_view_data("life", 810, 100, 30, 30))
        self.obj_rect_list.append(create_image_view_data("life", 850, 100, 30, 30))
        self.obj_rect_list.append(create_image_view_data("life", 890, 100, 30, 30))
        self.obj_rect_list.append(create_image_view_data("life", 930, 100, 30, 30))
        self.obj_rect_list.append(create_image_view_data("life", 970, 100, 30, 30))
        if self.obj_rect_list:
            obj_progress_data.extend(self.obj_rect_list)
        return obj_progress_data

    def debugging(self, is_debug: bool) -> list:  # 這個名字
        self.obj_rect_list = []
        if not is_debug:
            return
        for sprite in self.all_sprites:
            if isinstance(sprite, pygame.sprite.Sprite):
                top_left = sprite.rect.topleft
                points = [top_left, sprite.rect.topright, sprite.rect.bottomright
                    , sprite.rect.bottomleft, top_left]
                for index in range(len(points) - 1):
                    self.obj_rect_list.append(create_line_view_data("rect", *points[index], *points[index + 1], WHITE))

    def init_world(self):
        self.world = Box2D.b2.world(gravity=(0, 0), doSleep=True, CollideConnected=False)
        map = TiledMap_box2d(path.join(MAP_DIR, 'level_2.tmj'), 32)
        walls = map.get_wall_info()
        for wall in walls:
            vertices = map.transfer_to_box2d(wall)
            self.walls.add(Wall(vertices, self.world))
            # self.all_sprites.add(Wall(vertices, self.world))
        for wall in self.walls:
            vertices = [(wall.body.transform * v) for v in wall.box.shape.vertices]
            vertices = [map.trnsfer_box2d_to_pygame(v) for v in vertices]
            self.walls_info.append(create_polygon_view_data('wall', vertices, '#ffffff'))
        obj = map.load_other_obj()
        # x, y = (obj["car"][1] + (20 / 20), obj["car"][0] + (20 / 20))
        # self.car = Car(self.world, (26, 16),
        #                0, 3, 2)

        self.car = Car(self.world, (obj["car"][1], obj["car"][0]), 0, 3, 1)
        # end_p = End_point(self, (obj["end_point"][1], obj["end_point"][0]))
        self.all_sprites.add(self.car)
        # print(obj)
