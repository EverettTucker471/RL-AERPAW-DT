"""
@description Contains minimal functionality for computing SINR
values between devices in the AERPAW digial twin environment.
@start-date 9-7-2025
@updated 9-7-2025
@author(s) Everett Tucker
"""

import sionna
import math
import mitsuba as mi
import drjit as dr
import numpy as np
import tensorflow as tf
from typing import Tuple
from sionna.rt import Transmitter, Receiver, PlanarArray, PathSolver, RadioMapSolver, RadioMaterialBase
from EnvironmentFramework import Environment, GroundUser


class AERPAWEnv(Environment):
    """
    Extends the existing environment to provide specific functionality and configuration
    options for AERPAW operations, primarily channel modeling
    """

    def __init__(self, scene_path=None, uavs=None, ground_users=None, base_stations=None, temperature=290):
        """
        Creates a new AERPAW minimal environment with the configurations in config
        
        Args:
            scene_path (str): The path to the XML export to use to configure
            the physical environment, default to a flat, empty ground

            devices (list(dict)): A list config dictionaries for UAV devices, ex
            {"device_type": "tx",
            "mass": 1,
            "efficiency": 0.8,
            "position": np.array([10, 10, 50]),
            "velocity": np.array([0, 5, 0]),
            "color": np.array([1, 0, 0]),
            "bandwidth": 50,
            "rotor_area": 2,
            "signal_power": 3,
            "throughput_capacity": 625000000,
            "battery_capacity": 10000}

            ground_users (list(dict)): A list of config dictionaries for Ground Users, ex
            {"position": np.zeros(3),
            "velocity": np.zeros(3),
            "bandwidth": 50,
            "device_type": "rx",
            "color": np.zeros([0, 1, 0]),
            "desired_throughput": 375000}

            base_stations (list(dict)): A list of config dictionaries for Base Stations, ex
            {"device_type": "tx",
            "position": np.zeros(3),
            "velocity": np.zeros(3),
            "color": np.zeros([0, 0, 1]),
            "bandwidth": 50,
            "signal_power": 3,
            "throughput_capacity": 625000000,
            "battery_capacity": 10000}

            temperature (float): The temperature of the ambient environment in Kelvin, used
            for path loss calculation, default 290 Kelvin (17 C, 62 F)
        """
        # Substituting default scene
        if scene_path is None:
            scene_path = sionna.rt.scene.simple_reflector

        # Creating the inital scene, objects will be populated later
        super().__init__(scene_path, temperature=temperature)

        if uavs:
            for uav_config in uavs:
                self.addUAV(device_type=uav_config.get("device_type", None),
                                mass=uav_config.get("mass", 1),
                                efficiency=uav_config.get("efficiency", 0.8),
                                pos=uav_config.get("position", np.zeros(3)),
                                vel=uav_config.get("velocity", np.zeros(3)),
                                color=uav_config.get("color", np.array([1, 0, 0])),
                                bandwidth=uav_config.get("bandwidth", 50),
                                rotor_area=uav_config.get("rotor_area", None),
                                signal_power=uav_config.get("signal_power", 1),
                                throughput_capacity=uav_config.get("througput_capacity", 625000000),
                                battery_capacity=uav_config.get("battery_capacity", 10000))
                
        if ground_users:
            id = 0
            for gu_config in ground_users:
                self.gus.append(GroundUser(
                    id=id,
                    positions=gu_config.get("position", np.zeros(3)).reshape(1, 3),
                    initial_velocity=gu_config.get("velocity", np.zeros(3)),
                    height=gu_config.get("position", np.zeros(3))[2],
                    bandwidth=gu_config.get("bandwidth", 50),
                    com_type=gu_config.get("device_type", "rx"),
                    delta_t=self.delta_t,
                    color=gu_config.get("color", np.array([0, 1, 0])),
                    desired_throughputs=np.array([gu_config.get("desired_throughput", 375000)])
                    ))
                self.gus[id].lookAt()
                self.scene.add(self.gus[id].device)
                if self.gus[id].com_type == "tx":
                    self.n_tx += 1
                else:
                    self.n_rx += 1
                id += 1

        if base_stations:
            for bs_config in base_stations:
                self.addBaseStation(
                    device_type=bs_config.get("device_type", "tx"),
                    pos=bs_config.get("position", np.zeros(3)),
                    color=bs_config.get("color", np.array([0, 0, 1])),
                    bandwidth=bs_config.get("bandwidth", 50),
                    signal_power=bs_config.get("signal_power", 3),
                    throughput_capacity=bs_config.get("throughput_capacity", 625000000),
                    battery_capacity=bs_config.get("battery_capacity", 10000))


    def getSNR(self, max_depth=2, num_samples=1000000, sampling_frequency=1.0, mode="gpu", los=False, reverse=False):
        """
        Returns a dictionary of the SINR values between all pairs of transmitters and receivers
        
        Args:
            max_depth (int): The maximum number of reflections to consider while ray tracing, ignored if los is True, default 2
            num_samples (int): The number of sample rays to compute when ray tracing, ignored if los is True, default 1,000,000
            sampling_frequency (float): The frequency at which the channel impulse response is sampled at in Hz, default 1.0
            mode (str): The type of processor to use for ray tracing, either "cpu" or "gpu", default "gpu"
            los (bool): If you just want to compute the SNR over Line-of-Sight paths, default False
            reverse (bool): If you want to ray trace from recievers to transmitters, default False



        Return:
            (dict(dict(float))): A dictionary mapping all transmitters to a dictionary of SNR values for each receiver
        """
        # Generating dictionary from array
        tx_names = [tx for tx in self.scene.transmitters]
        rx_names = [rx for rx in self.scene.receivers]

        paths = self.computeLOSPaths(mode) if los else self.computeGeneralPaths(max_depth, num_samples, mode)
        snr = self.computeSNR(paths, sampling_frequency, reverse)

        rtn = {}
        for i in range(self.n_rx):
            row = {}
            for j in range(self.n_tx):
                row[tx_names[j]] = snr[i][j]
            rtn[rx_names[i]] = row
        
        return rtn
