import math


def preprocess(input_path, output_path, offset, buildings=False, z_off=None):
    with open(input_path, 'r') as infile, open(output_path, 'w') as outfile:    
        lines = infile.readlines()

        # Vertical scale factor for the building vertices
        z_exag = 4

        i = 100
        for line in lines:
            tokens = line.strip().split()

            try:
                vals = tokens[0].split("e+")
                
                assert len(vals) == 2

                for i in range(3):
                    # Implementing z-exaggeration
                    if i == 2 and buildings:
                        height = float(tokens[i]) - z_off
                        outfile.write(str(height * z_exag + 32) + " ")
                    elif i == 2:
                        outfile.write(str((float(tokens[i]) - offset[i]) * 1.5) + " ")
                    else:
                        outfile.write(str(float(tokens[i]) - offset[i]) + " ")
                for i in range(3, 6):
                    outfile.write(str(int(tokens[i])) + " ")
                for i in range(6, 9):
                    outfile.write(str(float(tokens[i])) + " ")
                outfile.write("\n")
            except:
                outfile.write(line)


def main():
    # Computing offset
    with open("/home/everetttucker471/Documents/RL-AERPAW-DT/LiDAR/meshes-01-30/meshes/terrain-mesh-small.ply", "r") as f:
        offset = [math.inf for _ in range(3)]
        for line in f.readlines():
            tokens = line.strip().split()
            if len(tokens) == 17:
                try:
                    float(tokens[0])  # Checking for conversion exception

                    for i in range(3):
                        offset[i] = min(offset[i], float(tokens[i]))
                except:
                    # Not one of the lines we want to consider
                    pass

    # Computing z-offset for buildings
    with open("/home/everetttucker471/Documents/RL-AERPAW-DT/LiDAR/meshes-01-30/meshes/building-mesh.ply", "r") as f:
        z_offset = math.inf
        for line in f.readlines():
            tokens = line.strip().split()

            if len(tokens) == 17:
                z_offset = min(z_offset, float(tokens[2]))
                    
    print(f'using offset: {offset}')
    print(f"using z-offset: {z_offset}")

    for input in ["building-mesh", "terrain-mesh-small"]:
        input_file = "/home/everetttucker471/Documents/RL-AERPAW-DT/LiDAR/meshes-01-30/meshes/" + input + ".ply"
        output_file = "/home/everetttucker471/Documents/RL-AERPAW-DT/LiDAR/meshes-01-30/meshes/" + input + "-output.ply"

        try:
            preprocess(input_file, output_file, offset, buildings=("building" in input_file), z_off=z_offset)
            print(f"Successfully converted {input_file} to {output_file}")
        except Exception as e:
            print(f"Error processing file: {e}")


if __name__ == "__main__":
    main()
