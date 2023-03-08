# Don't Touch

![Dont_touch](https://img.shields.io/github/v/tag/yen900611/Dont_touch)
[![Python 3.9](https://img.shields.io/badge/python-3.9-blue.svg)](https://www.python.org/downloads/release/python-390/)
[![MLGame](https://img.shields.io/badge/MLGame->9.5.3.*-<COLOR>.svg)](https://github.com/PAIA-Playful-AI-Arena/MLGame)
[![pygame](https://img.shields.io/badge/pygame-2.0.1-<COLOR>.svg)](https://github.com/pygame/pygame/releases/tag/2.0.1)

不要碰！
Don't Touch 是一款基於 MLGame 框架的遊戲，由玩家控制車子的輪子轉速，達到讓車子前進、後退、轉彎的效果，並且車子上配備有距離感測器，可以讓玩家了解車子與周遭牆壁的距離。玩家需要盡可能減少碰到牆壁的次數，並且走到迷宮的終點。
![](https://i.imgur.com/Rm5QGmC.gif)


---
## 目標

在遊戲時間截止前到達迷宮的終點，並且盡可能減少碰撞牆壁的次數。

### 排名條件

1. 自走車所走的距離。經過的檢查點愈多則排名愈前。
2. 自走車與牆壁碰撞次數。若兩車走經的檢查點數量相同，則碰撞次數少者排名愈前。
3. 自走車前進速度。若前兩項評分依據街平手，則比較走到最末檢查點時的遊戲時間，愈早走到者排名愈前。

## 遊戲系統

1. 行動機制

    控制左右輪轉速，達到前進、後退、轉彎的目的。
    左輪與右輪的轉速由玩家程式控制，範圍為 -255 ~ 255。 
   速度為 0 時相當於停在原地，速度為負值實則輪子向後轉，速度為正時輪子向前轉。

2. 感測器
    感測器測量的起點為自走車車身外圍，終點為直線距離上最靠的牆壁，實際距離如圖所示
    ![](https://i.imgur.com/ZjVxo2P.png)

4. 物件大小
    使用Box2D的座標系統，單位為cm，每公分換算為4像素


    - 自走車 12.5 x 10cm
    - 檢查點 20 x 20cm
    - 終點 15 x 15cm
4. 座標系統
    
    原點在迷宮區域的左上角，Ｘ軸向右為正，Y軸向上為正。
    ![](https://i.imgur.com/4dcUjgr.png)

---

# 進階說明

## 執行方式
運行於MLGame之下
* 搭配[MLGame](https://github.com/PAIA-Playful-AI-Arena/MLGame)執行，請將遊戲放在MLGame/games資料夾中，遊戲資料夾需命名為**Dont_touch**
```
# 在 `MLGame` 資料夾中
python -m mlgame -f 60 -i games/dont_touch/ml/ml_play.py -i games/dont_touch/ml/ml_play_manual.py games/dont_touch --time_to_play 1800 --map 2 --sound on
```
### 遊戲參數
* `map`：選擇不同的迷宮，目前提供6種迷宮地圖，迷宮編號從1開始，預設為1號地圖。
* `time_to_play`：限制遊戲總時間，單位為 frame，時間到了之後即使有玩家還沒走出迷宮，遊戲仍然會結束。
* `sensor`：選擇感測器數量，目前可以選擇4或6個，預設為6。
* `sound`：音效設定，可選擇"on"或"off"，預設為"off"


## ＡＩ範例

```python
class MLPlay:
    def __init__(self, ai_name,*args,**kwargs):
        self.player_no = ai_name
        self.r_sensor_value = 0
        self.l_sensor_value = 0
        self.f_sensor_value = 0
        self.control_list = {"left_PWM" : 0, "right_PWM" : 0}
        # print("Initial ml script")
        print(kwargs)

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

    def reset(self):
        """
        Reset the status
        """
        # print("reset ml script")
        pass

```

## 遊戲資訊

- `scene_info` 的資料格式如下

```json
{
    "frame": 16,
    "status": "GAME_ALIVE", 
    "x": 107.506, 
    "y": -112.5, 
    "angle": 0.0, 
    "R_sensor": 5.6, 
    "L_sensor": 4.7, 
    "F_sensor": 87.6, 
    "L_T_sensor": -1, 
    "R_T_sensor": -1, 
    "end_x": 12.5,
    "end_y": -12.5,
    "crash_times":1,
    "check_points": [(10, 50), (34, 20)]
}

```

* `frame`：遊戲畫面更新的編號
* `status`： 目前遊戲的狀態
    - `GAME_ALIVE`：遊戲進行中
    - `GAME_PASS`：遊戲通關
    - `GAME_OVER`：遊戲結束
* `x`：玩家自己車子的x座標，該座標系統原點位於迷宮左上角，x軸向右為正。
* `y`：玩家自己車子的y座標，該座標系統原點位於迷宮左上角，y軸向上為正。
* `angle`：玩家自己車子的朝向，車子向上為0度，數值逆時鐘遞增至360
* `R_sensor`：玩家自己車子右邊超聲波感測器的值，資料型態為數值
* `L_sensor`：玩家自己車子左邊超聲波感測器的值，資料型態為數值
* `F_sensor`：玩家自己車子前面超聲波感測器的值，資料型態為數值
* `L_T_sensor`：玩家自己車子左前超聲波感測器的值，資料型態為數值，單位是公分。
* `R_T_sensor`：玩家自己車子右前超聲波感測器的值，資料型態為數值
* `end_x`：終點x座標，該座標系統原點位於迷宮左上角，x軸向右為正。
* `end_y`：終點y座標，該座標系統原點位於迷宮左上角，y軸向上為正。
* `crash_times`：玩家此局遊戲中碰撞牆壁的次數，資料型態為數值。
* `check_points`:遊戲在必經的地方設置數個檢查點，此資料包含所有檢查點的座標，資料型態為列表。

座標資訊請參考 `座標系統` 章節
## 動作指令

- 在 update() 最後要回傳一個字典，資料型態如下。
    ```python
    {
            'left_PWM': 0,
            'right_PWM': 0
    }
    ```
    其中`left_PWM`與`right_PWM`分別代表左輪與右輪的馬力，接受範圍為-255~255。


## 遊戲結果

- 最後結果會顯示在console介面中，若是PAIA伺服器上執行，會回傳下列資訊到平台上。

|player|rank|frame_limit|used_frame|frame_percent|
|-|-|-|-|-|
|1P|1|1200|1136|94.66|

|total_checkpoints|check_points|remain_points|pass_percent|crush_times|score|
|-|-|-|-|-|-|
|8|8|0|100|2|79978.864|

- `frame_used`：表示遊戲使用了多少個frame
- `state`：表示遊戲結束的狀態
    - `FAIL`：遊戲失敗
    - `FINISH`：遊戲完成
- `attachment`：紀錄遊戲各個玩家的結果與分數等資訊
    - `player`：玩家編號
    - `rank`：排名
    - `used_frame`：個別玩家到達最後一個檢查點使用的frame數
    - `frame_limit`：該局遊戲所設定的時間上限
    - `frame_percent`：
        ![](https://i.imgur.com/QuI8HmM.png)
    - `total_checkpoints`：該地圖的總檢查點數量
    - `check_points`：玩家通過的檢查點數量
    - `pass_percent`：
        ![](https://i.imgur.com/QuMt5Lu.png)
    - `remain_percent`：
        ![](https://i.imgur.com/mym3FVm.png)
    - `crush_time`：玩家車子碰撞牆壁的次數
    - `score`：系統依據排名規則所計算之分數，分數愈高者排名愈前

###### tags: `PAIA GAME`