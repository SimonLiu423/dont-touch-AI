import pickle
import os
import sklearn.neighbors
from sklearn.metrics import mean_squared_error
from sklearn.model_selection import train_test_split
import numpy as np
from sklearn.tree import DecisionTreeRegressor
from sklearn.neighbors import KNeighborsRegressor
import math

path = "./log"
allFiles = os.listdir(path)
allFiles.sort()

data_set = []
prev_map = -1
cnt = 0
for file in allFiles:
    parse_file = file.split('_')
    map_id = int(parse_file[0])
    crashes = int(parse_file[1])
    frame_used = int(parse_file[2])
    # if frame_used > 3500:
    #     continue
    if prev_map == map_id:
        cnt += 1
        if cnt > 5:
            continue
    else:
        prev_map = map_id
        cnt = 0
    print(file, cnt)
    with open(os.path.join(path, file), "rb") as f:
        data_set.append(pickle.load(f))

# feature
f_sensor = []
l_sensor = []
r_sensor = []
lt_sensor = []
rt_sensor = []
x_pos = []
y_pos = []
angle = []
Y = []

for data in data_set:
    for i, sceneInfo in enumerate(data["scene_info"]):
        f_sensor.append(data["scene_info"][i]["F_sensor"])
        l_sensor.append(data["scene_info"][i]["L_sensor"])
        r_sensor.append(data["scene_info"][i]["R_sensor"])
        lt_sensor.append(data["scene_info"][i]["L_T_sensor"])
        rt_sensor.append(data["scene_info"][i]["R_T_sensor"])
        x_pos.append(data["scene_info"][i]["x"])
        y_pos.append(data["scene_info"][i]["y"])
        angle.append(data["scene_info"][i]["angle"])

        Y.append([data["action"][i]["left_PWM"], data["action"][i]["right_PWM"]])

Y = np.array(Y)
X = np.array([0, 0, 0, 0, 0, 0, 0, 0])
for i in range(len(f_sensor)):
    # X = np.vstack((X, [f_sensor[i], l_sensor[i], r_sensor[i], angle[i], target_angle[i], stuck_cnt[i], direction[i],
    #                    angle_diff[i]]))
    X = np.vstack((X, [f_sensor[i], l_sensor[i], r_sensor[i], lt_sensor[i], rt_sensor[i], x_pos[i], y_pos[i], angle[i]]))
X = X[1::]
print(X.shape, Y.shape)
print(X, Y)

# training
x_train, x_test, y_train, y_test = train_test_split(X, Y, test_size=0.2)

model = DecisionTreeRegressor()
model.fit(x_train, y_train)

# evaluation
y_predict = model.predict(x_test)
mse = mean_squared_error(y_test, y_predict)
print(mse)
rmse = math.sqrt(mse)
print("RMSE=%.2f" % rmse)

# save model
if not os.path.exists(os.path.dirname(__file__) + "/save"):
    os.makedirs(os.path.dirname(__file__) + "/save")
with open(os.path.join(os.path.dirname(__file__), 'save', "model.pickle"), 'wb') as f:
    pickle.dump(model, f)
