from mlgame.view.view_model import create_asset_init_data
from .math_function import cross_point_dot
import math

from .sensor import Sensor
import pygame
from .env import *


class Car(pygame.sprite.Sprite):
    def __init__(self, world, coordinate: tuple, car_no: int, sensor_num, angle: int):
        pygame.sprite.Sprite.__init__(self)
        self.car_no = car_no  # From 0 to 3
        self.image_num = 9
        self.image_name = f"car_0{self.car_no+1}"
        self.collide_frame = -100
        self.collide_times = 0
        self.size = (40, 40)  # car size
        self.is_completed = False
        self.end_frame = 0
        self.origin_image = pygame.transform.scale(
            pygame.image.load(path.join(ASSET_IMAGE_DIR, f"car_0{self.car_no+1}.png")),
            self.size)
        self.image = self.origin_image  # after rotate
        self.rect = self.image.get_rect()
        self.is_running = True
        self.status = "GAME_ALIVE"
        self.sensor_R = {"coordinate": (0, 0), "distance": -1}
        self.sensor_L = {"coordinate": (0, 0), "distance": -1}
        self.sensor_R_T = {"coordinate": (0, 0), "distance": -1}
        self.sensor_L_T = {"coordinate": (0, 0), "distance": -1}
        self.sensor_F = {"coordinate": (0, 0), "distance": -1}
        self.sensor_B = {"coordinate": (0, 0), "distance": -1}
        self.L_PWM = 0
        self.R_PWM = 0
        self.rect.center = (0, 0)  # pygame
        self.x, self.y = coordinate
        self.body = world.CreateDynamicBody(position=coordinate)
        self.box = self.body.CreatePolygonFixture(box=(1, 1), density=1, friction=0.1, restitution=0.3)
        self.sensor = Sensor(world, self.body, sensor_num, angle)
        self.body.angle = math.pi * angle
        self.check_point = 0
        self.explosion = False

    def update(self, commands):
        if self.explosion:
            self.image_name = f"regularExplosion0{self.image_num // 10}"
            self.image_num += 1
            if self.image_num == 60:
                self.image_num = 9
                self.explosion = False
                self.image_name = f"car_0{self.car_no+1}"
        self.image = pygame.transform.rotate(self.origin_image, (self.body.angle * 180 / math.pi) % 360)
        self.rect = self.image.get_rect()
        if self.is_running and commands != None:
            if commands['right_PWM'] > 255:
                self.R_PWM = 255
            elif commands['right_PWM'] < -255:
                self.R_PWM = -255
            else:
                self.R_PWM = commands['right_PWM']
            if commands['left_PWM'] > 255:
                self.L_PWM = 255
            elif commands['left_PWM'] < -255:
                self.L_PWM = -255
            else:
                self.L_PWM = commands['left_PWM']
            self.left_move(self.L_PWM)
            self.right_move(self.R_PWM)
        else:
            self.body.linearVelocity = (0, 0)

    def collide(self, frame):
        if frame - self.collide_frame > 120:
            self.collide_times += 1
            self.collide_frame = frame
            self.explosion = True
            return True
        return False


    def detect_distance(self, frame, walls):
        sensor_value = self.sensor.update(frame, walls)
        self.sensor_R = sensor_value["right_value"]
        self.sensor_L = sensor_value["left_value"]
        self.sensor_R_T = sensor_value["right_top_value"]
        self.sensor_L_T = sensor_value["left_top_value"]
        self.sensor_F = sensor_value["front_value"]
        self.sensor_B = sensor_value["rear_value"]

    def left_move(self, pwm: int):
        if pwm < 0:
            self.sensor.sensor_left.linearVelocity = self.body.GetWorldVector(localVector=(0, -(abs(pwm) ** 0.5)))
        else:
            self.sensor.sensor_left.linearVelocity = self.body.GetWorldVector(localVector=(0, pwm ** 0.5))

    def right_move(self, pwm: int):
        if pwm < 0:
            self.sensor.sensor_right.linearVelocity = self.body.GetWorldVector(localVector=(0, -(abs(pwm) ** 0.5)))
        else:
            self.sensor.sensor_right.linearVelocity = self.body.GetWorldVector(localVector=(0, pwm ** 0.5))

    def get_info(self):
        self.car_info = {"id": self.car_no,
                         "status": self.status,
                         "is_running": self.is_running,
                         "size": self.size,  # pygame
                         "topleft": self.rect.topleft,  # pygame
                         "center": self.rect.center,
                         "coordinate": (
                             round((self.body.position[0] - 1.145) * 5, 2),
                             round((self.body.position[1] + 1.145) * 5, 2)),
                         "angle": self.body.angle,  # Box2D
                         "r_sensor_value": self.sensor_R,
                         "l_sensor_value": self.sensor_L,
                         "r_t_sensor_value": self.sensor_R_T,
                         "l_t_sensor_value": self.sensor_L_T,
                         "f_sensor_value": self.sensor_F,
                         "b_sensor_value":self.sensor_B,
                         "L_PWM": self.L_PWM,
                         "R_PWM": self.R_PWM,
                         "end_frame": self.end_frame,
                         "image":self.image_name,
                         "crash_times":self.collide_times,
                         "check_point":self.check_point,
                         }
        return self.car_info
