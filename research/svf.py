import itertools
from hamming_weight import hamming_distance
from euclidean_distance import euclidean_distance, euclidean_distance2
import os
import numpy 
import math
import random
import datetime
import multiprocessing
import configparser

from itertools import groupby
from operator import itemgetter
from file_handler import open_json, write_file, store_plot, store_config
from utilities import conv_int
from scipy.stats.stats import pearsonr
import matplotlib.pyplot as plt

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

# Directory where files are stored.
SIDECHANNEL_TRACES_PATH = config["DEFAULT"]["SIDECHANNEL_TRACES_PATH"]

# Directory where results are stored.
RESULT_PATH = config["DEFAULT"]["RESULT_PATH_FORMAT"].format(date_now)

# START / END value that indicates where to start / end in the vcd file.
# If vcd file is large, you can select an interesting interval.
TIMESTAMP_START = int(config["DEFAULT"]["TIMESTAMP_START"])
TIMESTAMP_END = int(config["DEFAULT"]["TIMESTAMP_END"])

# Timestamp steps in vcd file.
TIMESTAMP_STEPS = int(config["DEFAULT"]["TIMESTAMP_STEPS"])


ALGORITHM = config["DEFAULT"]["ALGORITHM"]
HD_PATH = config["DEFAULT"]["HD_PATH"]

# Boolean whether we use all modules in vcd file.
ALL_MODULES = config["DEFAULT"].getboolean("ALL_MODULES")

def get_oracle_values(N, filename):
    with open(filename) as f:
        oracle_values = f.readlines()
        oracle_values = [int(x.strip()) for x in oracle_values] 
        return oracle_values[:N]

def pattern_extraction_oracle(oracle_values):
    combinations = []
    for comb in itertools.combinations(oracle_values, 2):
        combinations.append(comb)
    oracle_trace = []
    for comb in combinations:
        x = comb[0]
        y = comb[1]
        #xt = conv_int(x)
        hd = hamming_distance(x, y)
        #hd = euclidean_distance2(x, y)
        oracle_trace.append(hd)
    return oracle_trace

def run(module, oracles_list):
    data = {}
    oracle_vector_list = []
    for oracle in oracles_list:
        data["oracl"]
        svfs = {}
        svfs['max_svf'] = 0
        svfs['leak_count'] = 0  
        svf_values = {}
        coeffs = {}
        oracle_path = os.path.join(config["DEFAULT"]["vcd_file_basepath"], ALGORITHM, oracle + ".txt")
        oracle_values = get_oracle_values(NR_OF_VCD_FILES, oracle_path)
        oracle_vector = pattern_extraction_oracle(oracle_values)
        oracle_vector_list.append((oracle, oracle_vector))
    
    combinations = list(itertools.combinations(list(range(NR_OF_VCD_FILES)), 2))
    path = os.path.join(HD_PATH, module)
    cycles = open_json(path, "cycles.json")["cycles"]
    
    hd_files = []
    for comb in combinations:
        file_name = "HD_" + str(comb[0]) + "_" + str(comb[1]) + ".json"
        try:
            hd_file = open_json(path, file_name)
            hd_files.append(hd_file)
        except FileNotFoundError:
            pass
    print("N choose 2: {}".format(str(len(hd_files))))
    
    oracle_data = []
    
    for cycle in tqdm(range(1, cycles, 1), desc="Cycles completed", leave=False):
        hd_values = []
        for hd_file in hd_files:
            hd_value = hd_file[str(cycle)]
            hd_values.append(hd_value)
            
        for oracle, oracle_vector in oracle_vector_list:
            data["oracle"] = oracle
            value,_ = pearsonr(hd_values, oracle_vector)
            if not math.isnan(value):
                coeffs[cycle] = value
                svf_values[cycle] = value
            if value > svfs['max_svf']:
                svfs['max_svf'] = value
            if abs(value) > 0.3:
                svfs['leak_count'] = svfs['leak_count'] + 1
    svfs['values'] = svf_values
    
    json_path = os.path.join("svf", RESULT_PATH, "json", module)
    figure_path = os.path.join("svf", RESULT_PATH, "figure", module)
    name = "svf_" + test + "_" + str(NR_OF_VCD_FILES)
    write_file(json_path, name + ".json", svfs)
    store_plot(figure_path, name + '.png', coeffs, "svf")
    
def start_run(tasks):
    while not tasks.empty():
        module, oracles_list = tasks.get()
        print("Starting all oracles for module {}".format(oracles_list, module))
        run(module, oracles_list)

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

oracles = []
if ALGORITHM == "aes":
    oracles = ["sboxbyte1", "sboxbyte5", "fullro", "ro", "xor"]
elif ALGORITHM == "des":
    oracles = ["column", "or", "row", "sbox", "shift"]
elif ALGORITHM == "des2":
    oracles = ["column", "or", "row", "sbox", "and"]
elif ALGORITHM == "sha3":
    oracles = ["bc", "not", "xor"]

tasks = multiprocessing.Queue()
for module in modules:
    oracles_list = []
    for oracle in oracles:
        oracle_name = ALGORITHM + "_" + oracle + "_oracle"
        oracles_list.append(oracle_name)
    task = (module, oracles_list)
    print(task)
    tasks.put(task)
processes = [multiprocessing.Process(target=start_run, args=(tasks, )) for x in range(NR_OF_CORES)]

print("Starting processes.")
for p in processes:
    p.start()

# Waiting for processes.
for p in processes:
    p.join()
print("Processes finished.")