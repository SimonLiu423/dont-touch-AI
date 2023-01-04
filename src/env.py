from os import path

HEIGHT = 800
WIDTH = 1000

PPM = 20
TILESIZE = 32
'''sensor set trans'''
sensor_trans = ((1, 0),
                (0, 1),
                (-1, 0),
                (0, -1))

'''data path'''
GAME_DIR = path.dirname(__file__)
IMAGE_DIR = path.join(GAME_DIR, "../", "asset", "image")
SOUND_DIR = path.join(GAME_DIR, "../", "asset", "sound")
# MAP_DIR = path.join(GAME_DIR, "../", "src", "maps")
MAP_DIR = path.join(GAME_DIR,  "map")

'''color'''
BLACK = "#000000"
WHITE = "#ffffff"
RED = "#ff0000"
YELLOW = "#ffff00"
GREEN = "#00ff00"
GREY = "#8c8c8c"
BLUE = "#0000ff"
LIGHT_BLUE = "#21A1F1"
CYAN_BLUE = "#00FFFF"
PINK = "#FF00FF"
DARKGREY = "#282828"
LIGHTGREY = "#646464"
BROWN = "#643705"
FOREST = "#22390A"
MAGENTA = "#FF00FF"
MEDGRAY = "#4B4B4B"
ORANGE = "#FFA500"