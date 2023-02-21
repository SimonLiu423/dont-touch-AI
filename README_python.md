# 遊戲專案
[Github Dont_touch](https://github.com/yen900611/Dont_touch)

## 執行方式
## 運行於MLGame之下
* 搭配[MLGame](https://github.com/PAIA-Playful-AI-Arena/MLGame)執行，請將遊戲放在MLGame/games資料夾中，遊戲資料夾需命名為**Dont_touch**
```
# 在 `MLGame` 資料夾中
python -m mlgame -f 60 -i games/dont_touch/ml/ml_play.py -i games/dont_touch/ml/ml_play_manual.py games/dont_touch --time_to_play 1800 --map 2 --sound on
```
### 遊戲參數
* `map`：選擇不同的迷宮，目前提供6種迷宮地圖，迷宮編號從1開始，預設為1號地圖。
* `time_to_play`：限制遊戲總時間，單位為 frame，時間到了之後即使有玩家還沒走出迷宮，遊戲仍然會結束。
* `sensor`：選擇感測器數量，目前可以選擇3或5個，預設為5。
* `sound`：音效設定，可選擇"on"或"off"，預設為"off"


### 撰寫玩遊戲的程式

程式範例在 [`ml/ml_play_template.py`](https://github.com/yen900611/Dont_touch/blob/master/ml/ml_play_template.py)。


### 初始化參數
```python=2
    class MLPlay:
    def __init__(self, ai_name,*args,**kwargs):
        self.player_no = ai_name
        self.r_sensor_value = 0
        self.l_sensor_value = 0
        self.f_sensor_value = 0
        self.control_list = {"left_PWM": 0, "right_PWM": 0}
```
`ai_name`: 字串。其值只會是 `"1P"` 、 `"2P"` 、 `"3P"` 、 `"4P"`，代表這個程式被哪一台車使用。
`kwargs`:字典。裡面會包含遊戲的啟動參數。

### 遊戲場景資訊

由遊戲端發送的字典物件，同時也是存到紀錄檔的物件。
```python=17
def update(self, scene_info: dict, *args, **kwargs):
    """
    Generate the command according to the received scene information
    """
    if scene_info["status"] != "GAME_ALIVE":
        return "RESET"
    self.r_sensor_value = scene_info["R_sensor"]
    self.l_sensor_value = scene_info["L_sensor"]
    self.f_sensor_value = scene_info["F_sensor"]
    if self.f_sensor_value >15:
        self.control_list["left_PWM"] = 100
        self.control_list["right_PWM"] = 100
    else:
        self.control_list["left_PWM"] = 0
        self.control_list["right_PWM"] = 0
    return self.control_list

```
以下是該字典物件的鍵值對應：

* `"frame"`：整數。紀錄的是第幾影格的場景資訊
* `status`：玩家的遊戲狀態，一般情況為"GAME_ALIVE"，通過關卡則為"GAME_PASS"，到遊戲結束時尚未通關為"GAME_OVER"
* `"L_T_sensor"`：玩家自己車子左前超聲波感測器的值，資料型態為數值
* `"R_T_sensor"`：玩家自己車子右前超聲波感測器的值，資料型態為數值
* `"L_sensor"`：玩家自己車子左邊超聲波感測器的值，資料型態為數值
* `"F_sensor"`：玩家自己車子前面超聲波感測器的值，資料型態為數值
* `"R_sensor"`：玩家自己車子右邊超聲波感測器的值，資料型態為數值
* `"x"`：玩家自己車子的x座標，該座標系統原點位於迷宮左上角，x軸向右為正。
* `"y"`：玩家自己車子的y座標，該座標系統原點位於迷宮左上角，y軸向上為正。
* `"angle"`：玩家自己車子的朝向，車子向上為0度，數值逆時鐘遞增至360
* `end_x`：終點x座標，該座標系統原點位於迷宮左上角，x軸向右為正。
* `end_y`：終點y座標，該座標系統原點位於迷宮左上角，y軸向上為正。
* `crash_times`：玩家此局遊戲中碰撞牆壁的次數，資料型態為數值。
* `check_points`:遊戲在必經的地方設置數個檢查點，此資料包含所有檢查點的座標，資料型態為列表。

![](https://i.imgur.com/4dcUjgr.png)
* `angle`：玩家自己車子的絕對座標，該座標系統原點位於迷宮左上角，y軸向上為正。
![](https://i.imgur.com/CjycT8e.png)

### 遊戲指令

傳給遊戲端用來控制自走車的指令。

玩家透過字典`{"left_PWM" : 0, "right_PWM" : 0}`回傳左右輪的馬力，範圍為-255~255。


### 機器學習模式的玩家程式

自走車可以多人遊戲，所以在啟動機器學習模式時，需要利用 `-i <script_for_1P> -i <script_for_2P> -i <script_for_3P> -i <script_for_4P>` 指定最多六個不同的玩家程式。
* For example
```shell
python -m mlgame -i ./ml/ml_play_manual.py -i ./ml/ml_play_template.py  ./ 
```


![](https://i.imgur.com/ubPC8Fp.jpg)