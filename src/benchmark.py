import numpy as np
import time
import matplotlib.pyplot as plt
from AERPAWEnvironment import AERPAWEnv

import matplotlib.pyplot as plt

# Defining the scene, including receivers and transmitters

# Visualizing paths, this is the real test to see if rays bounce off the geometry of the environment
num_paths_list = []
time_list = []
num_rx_tx_list = []
trials = 8

for i in range(trials):
    num_rx_tx_list.append(i + 1)

    # Defining a generic UAV for simplicity
    generic_uav = {
        "device_type": "tx",
        "mass": 5,
        "efficiency": 0.7,
        "position": np.zeros(3),
        "velocity": np.zeros(3),
        "color": np.array([1, 0, 0]),
        "bandwidth": 50,
        "rotor_area": 0.25,
        "signal_power": 3,
        "throughput_capacity": 625000000,
        "battery_capacity": 10000
    }

    # Configuring some generic uavs with random x and y positions
    num_uavs = 3
    uavs = []
    for i in range(num_uavs):
        uav = dict(generic_uav)
        uav["position"] = np.array([np.random.rand() * 100 + 2125, np.random.rand() * 100 + 1800, 60])
        uavs.append(uav)

    # Generating Sample Base Stations

    # Defining a generic base station, then randomizing positions
    generic_base_station = {
        "device_type": "rx",
        "position": np.zeros(3),
        "color": np.array([0, 1, 0]),
        "bandwidth": 50,
        "signal_power": 10,
        "throughput_capacity": 625000000,
        "battery_capacity": 1000000
    }

    # Adding some base stations with random positions
    num_bs = 3
    bss = []
    for i in range(num_bs):
        bs = dict(generic_base_station)
        bs["position"] = np.array([np.random.rand() * 100 + 1900, np.random.rand() * 100 + 1850, 60])
        bss.append(bs)

    # Creating the scene with the sample devices
    env = AERPAWEnv(scene_path='/home/everetttucker471/Documents/RL-AERPAW-DT/LiDAR/meshes-02-03/lake-wheeler-scene.xml',
                    uavs=uavs, ground_users={}, base_stations=bss, temperature=300)
    env.visualize()

    start = time.time()
    general_paths = env.computeGeneralPaths(max_depth=3, num_samples=10 ** (i + 1), mode='gpu')
    end = time.time()
    time_list.append(end - start)
    num_paths_list.append(np.sum(general_paths.valid))


# plt.plot(num_rx_tx_list, num_paths_list, color="red", label="Path Count")
num_rx_tx_list = num_rx_tx_list[1:]
time_list = time_list[1:]
plt.plot(num_rx_tx_list, time_list, color="blue", label="Computation Time (s)")
plt.title("Computation Time (s) vs. Log Sample Count")
plt.legend(loc="best")
plt.show()
print(num_rx_tx_list, num_paths_list, time_list)
