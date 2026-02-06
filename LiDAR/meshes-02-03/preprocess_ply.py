import math


def preprocess_terrain(input_path, output_path, offset):
    with open(input_path, 'r') as infile, open(output_path, 'w') as outfile:    
        lines = infile.readlines()

        # Vertical scale factor for the building vertices
        z_exag = 4

        for line in lines:
            tokens = line.strip().split()

            if len(tokens) == 9:
                for i in range(3):
                    outfile.write(str(float(tokens[i]) - offset[i]) + " ")
                for i in range(3, 6):
                    outfile.write(str(int(tokens[i])) + " ")
                for i in range(6, 9):
                    outfile.write(str(float(tokens[i])) + " ")
                outfile.write("\n")
            else:
                outfile.write(line)


def preprocess_buildings(input_path, output_path, building_offset, offset):
    with open(input_path, 'r') as infile, open(output_path, 'w') as outfile:    
        lines = infile.readlines()

        for line in lines:
            tokens = line.strip().split()

            if len(tokens) == 9:
                for i in range(3):
                    outfile.write(str(float(tokens[i]) + building_offset[i] - offset[i]) + " ")
                for i in range(3, 6):
                    outfile.write(str(int(tokens[i])) + " ")
                for i in range(6, 9):
                    outfile.write(str(float(tokens[i])) + " ")
                outfile.write("\n")
            else:
                outfile.write(line)


def main():
    # Computing offset
    with open("/home/everetttucker/Documents/meshes-02-03/meshes/lake-wheeler-terrain-delauney.ply", "r") as f:
        offset = [math.inf for _ in range(3)]
        for line in f.readlines():
            tokens = line.strip().split()
            if len(tokens) == 9:
                try:
                    float(tokens[0])  # Checking for conversion exception

                    for i in range(3):
                        offset[i] = min(offset[i], float(tokens[i]))
                except:
                    # Not one of the lines we want to consider
                    pass
                    
    print(f'using offset: {offset}')

    for input in ["terrain-delauney"]:
        input_file = "/home/everetttucker/Documents/meshes-02-03/meshes/lake-wheeler-" + input + ".ply"
        output_file = "/home/everetttucker/Documents/meshes-02-03/meshes/lake-wheeler-" + input + "-output.ply"

        try:
            preprocess_terrain(input_file, output_file, offset)
            print(f"Successfully converted {input_file} to {output_file}")
        except Exception as e:
            print(f"Error processing file: {e}")
    
    return
    
    building_offset = [2088230.0000, 717856.0000, 80]
    for input in ["buildings-ascii"]:
        input_file = "/home/everetttucker/Documents/meshes-02-03/meshes/lake-wheeler-" + input + ".ply"
        output_file = "/home/everetttucker/Documents/meshes-02-03/meshes/lake-wheeler-" + input + "-output.ply"

        try:
            preprocess_buildings(input_file, output_file, building_offset, offset)
            print(f"Successfully converted {input_file} to {output_file}")
        except Exception as e:
            print(f"Error processing file: {e}")


if __name__ == "__main__":
    main()