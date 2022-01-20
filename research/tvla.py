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
import statistics
from itertools import groupby
from operator import itemgetter
from file_handler import open_json, write_file, store_plot, store_config, open_VCD
from utilities import conv_int, get_modules_names_list
from scipy.stats.stats import pearsonr, ttest_ind
import matplotlib.pyplot as plt

config_file = "config.ini"
config = configparser.ConfigParser()
config.read(config_file)
if config["DEFAULT"].getboolean("NOTEBOOK"):
    from tqdm.notebook import trange, tqdm # if running in a notebook
else:
    from tqdm import trange, tqdm # if not running in a notebook
    
date_now = datetime.datetime.now().strftime("%Y_%m_%d__%H_%M_%S")

NR_OF_VCD_FILES = int(config["DEFAULT"]["NR_OF_VCD_FILES"])
NR_OF_CORES = int(config["DEFAULT"]["NR_OF_CORES"])
VCD_FILE_FORMAT = config["DEFAULT"]["VCD_FILE_FORMAT"]
SIDECHANNEL_TRACES_PATH = config["DEFAULT"]["SIDECHANNEL_TRACES_PATH"]
RESULT_PATH = config["DEFAULT"]["RESULT_PATH_FORMAT"].format(date_now)
TIMESTAMP_START = int(config["DEFAULT"]["TIMESTAMP_START"])
TIMESTAMP_END = int(config["DEFAULT"]["TIMESTAMP_END"])
TIMESTAMP_STEPS = int(config["DEFAULT"]["TIMESTAMP_STEPS"])
ALGORITHM = config["DEFAULT"]["ALGORITHM"]
VCD_FILE_BASEPATH = config["DEFAULT"]["VCD_FILE_BASEPATH"]
VCD_FILE_PATH = os.path.join(VCD_FILE_BASEPATH, ALGORITHM) 
HD_PATH = config["DEFAULT"]["HD_PATH"]
TVLA_FIXED_PATH = os.path.join(config["DEFAULT"]["vcd_file_basepath"], ALGORITHM, "tvla_fixed", "traces")
ALL_MODULES = config["DEFAULT"].getboolean("ALL_MODULES")

def get_tvla_fixed(module):
    file_path = os.path.join(TVLA_FIXED_PATH, module)
    
    return list(open_json(file_path, "round_0.json").values())

def get_tvla_random(module):
    file_path = os.path.join(SIDECHANNEL_TRACES_PATH, module)
    randoms = []
    for i in range(NR_OF_VCD_FILES):
        random = list(open_json(file_path, "round_" + str(i) + ".json").values())
        randoms.append(random)
    return randoms

def run(module, test):
    fixed = get_tvla_fixed(module)
    randoms = get_tvla_random(module)
    svfs = {}
    svfs['max_svf'] = 0
    svfs['leak_count'] = 0
    coeffs = {}
    svf_values = {}
    for cycle in tqdm(range(1, len(fixed), 1), desc="Cycles completed", leave=False):
        random_values = []
        for random in randoms:
            #print(hds)
            v = int(random[cycle])
            random_values.append(v)
        value = float('nan')
        try:
            group1 = numpy.full(len(random_values),int(fixed[cycle]))
            group2 = random_values
            value,_ = ttest_ind(group1, group2)
            #print(group1, group2)
        except ZeroDivisionError:
            value = 0
        if not math.isnan(value):
            coeffs[cycle] = value
            svf_values[cycle] = value
        if value > svfs['max_svf']:
            svfs['max_svf'] = value
        if abs(value) > 4.5:
            svfs['leak_count'] = svfs['leak_count'] + 1
            #print("HD: ", hd_values)
    svfs['values'] = svf_values
    
    json_path = os.path.join("tvla", RESULT_PATH, "json", module)
    figure_path = os.path.join("tvla", RESULT_PATH, "figure", module)
    name = "tvla_" + test + "_" + str(NR_OF_VCD_FILES)
    write_file(json_path, name + ".json", svfs)
    print("Numer of cycles: {}".format(len(coeffs)))
    store_plot(figure_path, name + '.png', coeffs, "tvla")
    
def start_run(tasks):
    while not tasks.empty():
        module, test = tasks.get()
        print("Starting {} for module {}".format(test, module))
        run(module, test)

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

tasks = multiprocessing.Queue()
for module in modules:
    test_name = ALGORITHM
    tasks.put((module, test_name))
    
processes = [multiprocessing.Process(target=start_run, args=(tasks, )) for x in range(NR_OF_CORES)]

print("Starting processes.")
for p in processes:
    p.start()

# Waiting for processes.
for p in processes:
    p.join()
print("Processes finished.")