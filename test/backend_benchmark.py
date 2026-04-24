import sionna
import time
import numpy as np
import drjit as dr
import mitsuba as mi
from sionna.rt import Receiver, Transmitter, PathSolver, PlanarArray, load_scene


def create_transmitters(scene, num_tx):
    scene.transmitters.clear()
    for i in range(num_tx):
        scene.add(Transmitter(name=str(f"tx_{i}"), position=(0, 0, 0), velocity=(0, 0, 0)))
    scene.tx_array = PlanarArray(num_rows=1, num_cols=1, pattern="tr38901", polarization="V")


def create_receivers(scene, num_rx):
    scene.receivers.clear()
    for i in range(num_rx):
        scene.add(Receiver(name=str(f"rx_{i}"), position=(0, 0, 0), velocity=(0, 0, 0)))
    scene.rx_array = PlanarArray(num_rows=1, num_cols=1, pattern="tr38901", polarization="V")


def randomize_tx_positions(scene, num_tx):
    for i in range(num_tx):
        tx = scene.get(f"tx_{i}")
        tx.position = np.array([np.random.rand() * 100 + 2125, np.random.rand() * 100 + 1800, 60])


def randomize_rx_positions(scene, num_rx):
    for i in range(num_rx):
        rx = scene.get(f"rx_{i}")
        rx.position = np.array([np.random.rand() * 100 + 1900, np.random.rand() * 100 + 1850, 60])


def benchmark():
    scene_path = "/home/everetttucker471/Documents/RL-AERPAW-DT/LiDAR/meshes-02-03/lake-wheeler-scene.xml"
    scene = load_scene(scene_path)

    # Path Computation Hyperparameters
    max_depth = 3
    max_samples = 1000000
    sampling_frequency = 1.0

    # Environment Hyperparameters
    epochs = 10
    num_rx = 5
    num_tx = 5

    """
    On a RTX 3050 Laptop GPU with 6GB VRAM:
    For the typical case of 5 receivers and 5 transmitters, with a depth of 3 and 10^6 samples, we see
    * Memory Consumption: 1600 Mb
    * Time: 90ms
    """

    create_receivers(scene, num_rx)
    create_transmitters(scene, num_tx)
    time_results = []
    for i in range(epochs):
        randomize_rx_positions(scene, num_rx)
        randomize_tx_positions(scene, num_tx)
        
        start = time.time()

        dr.flush_malloc_cache()  # Freeing up memory, because this uses a lot

        # Setting the mitsuba variant depending on the computation mode
        mi.set_variant("cuda_ad_mono_polarized")

        # Computing Paths
        solver = PathSolver()
        paths = solver(scene, max_depth=max_depth, max_num_paths_per_src=max_samples, 
                      samples_per_src=max_samples, los=True, specular_reflection=True, 
                      diffuse_reflection=True, refraction=True)
        
        # Computing channel impulse response
        paths.cir(sampling_frequency=sampling_frequency, num_time_steps=1, reverse_direction=False)

        end = time.time()
        time_results.append(1000 * (end - start))
    
    print("Results For: ")
    print(f"{num_rx} Receivers")
    print(f"{num_tx} Transmitters")
    print(f'Max Depth: {max_depth}')
    print(f'Max Samples: {max_samples}')
    print("-" * 30)

    print(np.array(time_results, dtype=np.int32))


if __name__ == '__main__':
    benchmark()
    