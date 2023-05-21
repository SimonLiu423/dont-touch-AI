from rl.train import *

if __name__ == '__main__':
    N_MAPS = 12
    FRAME_LIMIT = 1800

    ai_name = "1P"
    mlplay = MLPlay(ai_name)

    while True:
        map_id = np.random.randint(1, N_MAPS)
        game = Dont_touch(1, map_id, FRAME_LIMIT, 5, "off")
        print("Training with map {}".format(map_id))
        while game.is_running and not quit_or_esc():
            scene_info = game.get_data_from_game_to_player()[ai_name]
            commands = {ai_name: mlplay.update(scene_info)}

            if scene_info["status"] in ("GAME_OVER", "GAME_PASS"):
                mlplay.reset()
                break
            game.update(game.get_keyboard_command())

