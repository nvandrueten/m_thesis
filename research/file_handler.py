from vcdvcd import VCDVCD
import json
import os
import matplotlib.pyplot as plt

# Open a .vcd file and parse the file.
# Returns a VCDVCD object.
def open_VCD(file_name):
    vcd = None
    try:
        print("Opening file: {}".format(file_name))
        vcd = VCDVCD(file_name,store_scopes=True)
        print("Opening file: {} successful".format(file_name))
    except FileNotFoundError:
        print("File {} not found.".format(file_name))
    except ValueError:
        print("File {} has incorrect format.".format(file_name))
    return vcd

# Writes a file called 'file_name'.
# Dumps a Hamming Distance dict as a json file.
def write_file(path, file_name, _dict):
    if path and not os.path.exists(path):
        print("Making directory: {} ".format(path))
        try:
            os.makedirs(path)
        except FileExistsError:
            print("Directory already exist. Race condition")
    
    file_path = os.path.join(path, file_name)
    #print("Storing in file: {}".format(file_path))
    with open(file_path, 'w') as outfile:
        json.dump(_dict, outfile)
    #print("Storing in file: {} successful".format(file_path))
    
def open_json(path, file_name):
    file_path = os.path.join(path, file_name)
    #print("Opening json file: {}".format(file_path))
    data = None
    with open(file_path) as infile:
        data = json.load(infile)
    #print("Opening file: {} successful".format(file_path))
    return data

def store_plot(path, file_name, _dict, method):
    if path and not os.path.exists(path):
        print("Making directory: {} ".format(path))
        try:
            os.makedirs(path)
        except FileExistsError:
            print("Directory already exist. Race condition")
    file_path = os.path.join(path, file_name)
    
    lists = sorted(_dict.items()) # sorted by key, return a list of tuples

    if(len(lists) > 0):
        x, y = zip(*lists) # unpack a list of pairs into two tuples


        lines = plt.scatter(x, y, s=1, marker="x")

        if method == "svf":
            plt.axhline(y = 0.3, color = 'r', linestyle = ':')
            plt.axhline(y = -0.3, color = 'r', linestyle = ':')
            plt.ylabel('SVF Value')
        elif method == "tvla":
            plt.axhline(y = 4.5, color = 'r', linestyle = ':')
            plt.axhline(y = -4.5, color = 'r', linestyle = ':')
            plt.ylabel('TVLA Value')
        #plt.plot(_dict.items())

        plt.xlabel('Cycle')
        plt.title(file_name)

        plt.savefig(file_path)
        plt.clf()
        #plt.show()

def store_config(config, config_file):
    with open(config_file, 'w') as configfile:
        config.write(configfile)
        print("Changed config file!")