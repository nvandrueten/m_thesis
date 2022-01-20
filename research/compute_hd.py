import os
import itertools
import multiprocessing
import datetime
import configparser
import math
import numpy

from hamming_weight import hamming_distance
from file_handler import open_json, write_file, store_config
from utilities import conv_int
from scipy.stats.stats import pearsonr

# Loading configuration file.
config_file = "config.ini"
config = configparser.ConfigParser()
config.read(config_file)
if config["DEFAULT"].getboolean("NOTEBOOK"):
    from tqdm.notebook import trange, tqdm # if running in a notebook
else:
    from tqdm import trange, tqdm # if not running in a notebook
    
date_now = datetime.datetime.now().strftime("%Y_%m_%d__%H_%M_%S")

# Number of vcd files.
NR_OF_VCD_FILES = int(config["DEFAULT"]["NR_OF_VCD_FILES"])

# Number of cores used.
NR_OF_CORES = int(config["DEFAULT"]["NR_OF_CORES"])

# Format of vcd files.
VCD_FILE_FORMAT = config["DEFAULT"]["VCD_FILE_FORMAT"]

# Directory where files are located.
SIDECHANNEL_TRACES_PATH = config["DEFAULT"]["SIDECHANNEL_TRACES_PATH"]

# Directory where files are stored.
HD_PATH = config["DEFAULT"]["HD_PATH_FORMAT"].format(date_now)
# Save HD path in configuration file. 
config.set('DEFAULT', 'HD_PATH', HD_PATH)

# START / END value that indicates where to start / end in the vcd file.
# If vcd file is large, you can select an interesting interval.
TIMESTAMP_START = int(config["DEFAULT"]["TIMESTAMP_START"])
TIMESTAMP_END = int(config["DEFAULT"]["TIMESTAMP_END"])

# Timestamp steps in vcd file.
TIMESTAMP_STEPS = int(config["DEFAULT"]["TIMESTAMP_STEPS"])

# Boolean whether we use all modules in vcd file.
ALL_MODULES = config["DEFAULT"].getboolean("ALL_MODULES")

# Open sidechannel trace n of module.
# "module" : Module name string
# "n" : integer.
def get_sidechannel_values(module, n):
    vcd_dump_file_name, vcd_dump_file_extension = os.path.splitext(os.path.split(VCD_FILE_FORMAT)[1])
    path =  os.path.join(SIDECHANNEL_TRACES_PATH, module)
    file = open_json(path, vcd_dump_file_name.format(n) + ".json")
    return file

# Starts 1 core process.
# Computes hamming distance between round i and round j for every module.
# "i": Integer
# "j": Integer
# "modules" : list of module name strings
def run(i, j, modules):
    max_cycles = 0
    for module in modules:
        values_i = get_sidechannel_values(module, i)
        values_j = get_sidechannel_values(module, j)
        if(len(values_i) > max_cycles):
            max_cycles = len(values_i)
        if(len(values_j) > max_cycles):
            max_cycles = len(values_j)
        hd_dict = {}
        for ctr in range(len(values_i)):
            key = str(TIMESTAMP_START + ctr * TIMESTAMP_STEPS)
            val_i = values_i[key]
            val_j = values_j[key]
            if (val_i is not None) and (val_j is not None):
                #print(val_i, type(val_i))
                #print(val_j, type(val_j))
                x = conv_int(val_i)
                y = conv_int(val_j)
                hd = hamming_distance(x, y)
                hd_dict[ctr] = hd
        path = os.path.join(HD_PATH, module)
        file_name = "HD_" + str(i) + "_" + str(j) + ".json"
        write_file(path, file_name, hd_dict)
        d = {}
        d['cycles'] = max_cycles
        write_file(path, "cycles.json", d)

# Start a run that takes a task from queue until the queue is empty.
# "tasks": Queue of integer tuple i and j.
# "modules" : list of module name strings
def start_run(tasks, modules):
    while not tasks.empty():
        i, j = tasks.get()
        print("Starting {}, {}".format(i, j))
        try:
            run(i, j, modules)
        except FileNotFoundError:
            pass
        
# Open a vcd file and get all module names.
# returns a list of module name strings.
def get_all_modules():
    vcd = open_VCD(os.path.join(VCD_FILE_PATH, VCD_FILE_FORMAT.format(0)))
    return get_modules_names_list(vcd)

# Returns a list of interesting modules for our research.
def get_research_modules():
    return [
        "TOP.mkTbSoc.soc_soc.ccore.dmem.dcache", # Data Cache
        "TOP.mkTbSoc.soc_soc.ccore.riscv.stage2.registerfile", # Register File
        "TOP.mkTbSoc.soc_soc.ccore.riscv.stage5.csr", # CSR
        "TOP.mkTbSoc.soc_soc.ccore.riscv.stage3.multicycle_alu", # ALU
        "TOP.mkTbSoc.soc_soc.ccore.riscv.stage3.multicycle_alu.fpu", #FPU
        "TOP.mkTbSoc.soc_soc.ccore.riscv.stage3.multicycle_alu.mbox", #Mul-Div Unit
        "TOP.mkTbSoc.soc_soc.ccore.riscv.stage0.bpu", # BPU
        "TOP.mkTbSoc.soc_soc.ccore.imem.icache", # Instruction cache
        "TOP.mkTbSoc.soc_soc.ccore.imem.itlb", # Instruction TLB
        "TOP.mkTbSoc.soc_soc.ccore.dmem.dtlb", # Data TLB   
    ]

modules = []
if ALL_MODULES:
    modules = get_all_modules()
else:
    modules = get_research_modules()
#modules = ["TOP.mkTbSoc.soc_soc.ccore.riscv.stage3.multicycle_alu"]
for module in modules:
    path = os.path.join(HD_PATH, module)
    os.makedirs(path)
    
# Computes (NR_OF_VCD_FILES choose 2) combinations.
combinations = list(itertools.combinations(list(range(NR_OF_VCD_FILES)), 2))

print("[INFO] VCD files: {}".format(NR_OF_VCD_FILES))
print("[INFO] VCD timestamps: from {} to {}".format(TIMESTAMP_START, TIMESTAMP_END))
print("[INFO] Number of cores: {}".format(NR_OF_CORES))
print("[INFO] Reading traces in directory: {}".format(SIDECHANNEL_TRACES_PATH))
print("[INFO] Storing HD in directory: {}".format(HD_PATH))
print("[INFO] Modules: {}".format(len(modules)))
print("[INFO] Combinations: {}".format(combinations))

# Create a queue for every combination possible.
tasks = multiprocessing.Queue()
for combination in combinations:
    tasks.put(combination)

processes = [multiprocessing.Process(target=start_run, args=(tasks, modules,)) for x in range(NR_OF_CORES)]

print("Starting processes.")
for p in processes:
    p.start()

# Waiting for processes.
for p in processes:
    p.join()
print("Processes finished.")
store_config(config, config_file)