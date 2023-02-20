from os import path

PPM = 20.0  # pixels per meter
TARGET_FPS = 60
TIME_STEP = 1.0 / TARGET_FPS

'''width and height'''
WIDTH = 1000
HEIGHT = 800
TILE_WIDTH = 540  # 大小
TILE_HEIGHT = 540

'''tile-base'''
TILESIZE = 20
TILE_LEFTTOP = 20, 20  # pixel
GRIDWIDTH = (TILE_WIDTH + TILE_LEFTTOP[0]) / TILESIZE
GRIDHEIGHT = (TILE_HEIGHT + TILE_LEFTTOP[1]) / TILESIZE

'''sensor set trans'''
sensor_trans = ((1, 0),
                (0, 1),
                (-1, 0),
                (0, -1))

'''environment data'''
FPS = 30

'''color'''
WHITE = "#ffffff"
RED = "#ff0000"

'''object size'''
car_size = (60, 30)

'''data path'''
ASSET_IMAGE_DIR = path.join(path.dirname(__file__), "../asset/image")
IMAGE_DIR = path.join(path.dirname(__file__), 'image')
SOUND_DIR = path.join(path.dirname(__file__), '../asset/sound')
MAP_DIR = path.join(path.dirname(__file__),  "map")

'''image'''
BG_IMG = "bg.png"
BG_URL = "https://github.com/yen900611/dont_touch/blob/master/asset/image/bg.png"

LOGO = "logo.png"
LOGO_URL = "https://github.com/yen900611/dont_touch/blob/master/asset/image/logo.png"
