from os import path

from src.tiledMap_to_box2d import TiledMap_box2d

if __name__ == "__main__":
    map_folder = path.join(path.dirname(__file__), "src/map")
    map = TiledMap_box2d(path.join(map_folder, 'level_2.tmj'), 32)
    # map.print_data()
    map.get_wall_info()
    # map.transfer_to_box2d([[18, 0, 1], [19, 0, 0]])
