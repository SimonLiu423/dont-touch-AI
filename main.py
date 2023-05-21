from rl.train import *
import pygame
import pandas as pd
from mlgame.view.view import PygameView

if __name__ == '__main__':
    N_MAPS = 12
    FRAME_LIMIT = 1800

    render = True

    ai_name = "1P"
    mlplay = MLPlay(ai_name)

    pygame.init()
    while True:
        map_id = np.random.randint(1, N_MAPS)
        game = Dont_touch(1, map_id, FRAME_LIMIT, 5, "off")

        if render:
            scene_init_info_dict = game.get_scene_init_data()
            game_view = PygameView(scene_init_info_dict)

        print("Training with map {}".format(map_id))
        while game.is_running and not quit_or_esc():
            scene_info = game.get_data_from_game_to_player()[ai_name]
            commands = {ai_name: mlplay.update(scene_info)}

            game.update(commands)

            if render:
                game_progress_data = game.get_scene_progress_data()
                game_view.draw(game_progress_data)

        mlplay.reset()
        if render:
            game_view.reset()

        game_result = game.get_game_result()
        attachments = game_result['attachment']
        print(pd.DataFrame(attachments).to_string())

