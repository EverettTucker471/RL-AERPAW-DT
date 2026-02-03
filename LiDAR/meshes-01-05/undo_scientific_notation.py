import math

def preprocess(input_path, output_path, offset):    
    with open(input_path, 'r') as infile, open(output_path, 'w') as outfile:
        lines = infile.readlines()

        if "2" not in input_path and "animal" in input_path:
            lines = lines[:25341]
        if "external" in input_path:
            lines = lines[:5100748]
        for line in lines:
            tokens = line.strip().split()

            try:
                vals = tokens[0].split("e+")
                
                assert len(vals) == 2

                tokens[0] = str(round(float(vals[0]) * 10 ** int(vals[1])))
                
                for i in range(3):
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

    with open("/home/everetttucker471/Documents/RL-AERPAW-DT/LiDAR/meshes-01-05/meshes/external-mesh.ply", "r") as f:
        offset = [math.inf for i in range(3)]
        for line in f.readlines():
            tokens = line.strip().split()
            if len(tokens) == 9:
                try:
                    val = float(tokens[0])

                    for i in range(3):
                        offset[i] = min(offset[i], float(tokens[i]))
                except:
                    # Not one of the lines we want to consider
                    pass
                    
    print(f'using offset: {offset}')

    for input in ["animal-health-mesh", "animal-health-2-mesh", "external-mesh"]:
        input_file = "/home/everetttucker471/Documents/RL-AERPAW-DT/LiDAR/meshes-01-05/meshes/" + input + ".ply"
        output_file = "/home/everetttucker471/Documents/RL-AERPAW-DT/LiDAR/meshes-01-05/meshes/" + input + "-output.ply"
    
        try:
            preprocess(input_file, output_file, offset)
            print(f"Successfully converted {input_file} to {output_file}")
        except Exception as e:
            print(f"Error processing file: {e}")

if __name__ == "__main__":
    main()