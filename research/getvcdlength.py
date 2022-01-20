from file_handler import open_VCD
import os
import configparser

config = configparser.ConfigParser()
config.read('config.ini')

VCD_FILE_BASEPATH = config["DEFAULT"]["VCD_FILE_BASEPATH"]
VCD_FILE_FORMAT = config["DEFAULT"]["VCD_FILE_FORMAT"]

METHOD = config["DEFAULT"]["METHOD"]
ALGORITHM = config["DEFAULT"]["ALGORITHM"]

path = os.path.join(VCD_FILE_BASEPATH, ALGORITHM)
print(path)
if METHOD == "tvla" and config["DEFAULT"].getboolean("tvla_fixed"):
    path = os.path.join(path, "tvla_fixed") 

filenr = 0    
if METHOD == "svf":
    if ALGORITHM == "aes":
        filenr = 152
    elif ALGORITHM == "des":
        filenr = 241
    elif ALGORITHM == "des2":
        filenr = 205
    elif ALGORITHM == "sha3":
        filenr = 141
path = os.path.join(path, VCD_FILE_FORMAT.format(filenr))
print(path)
vcd = open_VCD(path)
print(vcd.endtime)