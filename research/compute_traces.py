import json
import os
import gc
import itertools
import multiprocessing
import datetime
import configparser

from utilities import get_modules_names_list, signal_access, get_value_signal_dict, get_signal_dict, concat, chunkIt, conv_int
from hamming_weight import hamming_weight, hamming_distance
from file_handler import open_VCD, write_file, open_json, store_config

#pip install vcdvcd numpy scipy tqdm matplotlib
from vcdvcd import VCDVCD 
import numpy 
import scipy 
from scipy.special import comb
from scipy.stats.stats import pearsonr

# Loading configuration file.
config_file = "config.ini"
config = configparser.ConfigParser()
config.read(config_file)

date_now = datetime.datetime.now().strftime("%Y_%m_%d__%H_%M_%S")

if config["DEFAULT"].getboolean("NOTEBOOK"):
    from tqdm.notebook import trange, tqdm # if running in a notebook
else:
    from tqdm import trange, tqdm # if not running in a notebook

# Timestamp steps in vcd file.
TIMESTAMP_STEPS = int(config["DEFAULT"]["TIMESTAMP_STEPS"])

# START / END value that indicates where to start / end in the vcd file.
# If vcd file is large, you can select an interesting interval.
TIMESTAMP_START = int(config["DEFAULT"]["TIMESTAMP_START"])
TIMESTAMP_END = int(config["DEFAULT"]["TIMESTAMP_END"])

# Number of cores used.
NR_OF_CORES = int(config["DEFAULT"]["NR_OF_CORES"])

# Number of vcd files.
NR_OF_VCD_FILES = int(config["DEFAULT"]["NR_OF_VCD_FILES"])

# Directory where files are stored.
SIDECHANNEL_TRACES_PATH = config["DEFAULT"]["SIDECHANNEL_TRACES_PATH_FORMAT"].format(date_now)

# Boolean whether we use all modules in vcd file.
ALL_MODULES = config["DEFAULT"].getboolean("ALL_MODULES")

# Save traces path in configuration file. 
config.set("DEFAULT", "SIDECHANNEL_TRACES_PATH", SIDECHANNEL_TRACES_PATH)

# Basepath of where vcd files are stored.
# VCD_FILE_BASEPATH
#   |-- aes
#        |-----tvla_fixed
#                   |--------round_0.vcd
#         | round_0.vcd
#         | round_1.vcd
#         | ...
#         | aes_sbox1_oracle.txt
#          | ...
#   |-------- des
#
#
#
#   |-------- des2
#
#
#   |-------- sha3
VCD_FILE_BASEPATH = config["DEFAULT"]["VCD_FILE_BASEPATH"]

# Format of vcd files.
VCD_FILE_FORMAT = config["DEFAULT"]["VCD_FILE_FORMAT"]

# Method used: svf/tvla
METHOD = config["DEFAULT"]["METHOD"]

# Algorithm used: aes/dex
ALGORITHM = config["DEFAULT"]["ALGORITHM"]

# Path where vcd file are stored, uses the basepath and algorithm.
VCD_FILE_PATH = os.path.join(VCD_FILE_BASEPATH, ALGORITHM) 
if METHOD == "tvla" and config["DEFAULT"].getboolean("TVLA_FIXED"):
        VCD_FILE_PATH = os.path.join(VCD_FILE_PATH, "tvla_fixed")
        NR_OF_VCD_FILES = 1
        
# Computes side-channel trace of 1 module 
# "vcd" : vcdvcd object.
# "module" : String of module name.
def compute_sidechannel_trace(vcd, module):  
    module_dict = {}

    # Get signals of this module.
    signals = signal_access(vcd, module)
    endtime = vcd.endtime
    value = None

    # Iterate through every signal in this module.
    for signal in tqdm(signals, desc="Signals completed", leave=False):
        # sig_tv contains a time-value tuple when signal changes value. 
        sig_tv = signal.tv
        signal_dict = get_signal_dict(sig_tv)
        # Start value is None, we do not know the signal value.
        current_sig_value = None

        # Iterate through every timestamp.
        for timestamp in itertools.chain(range(TIMESTAMP_START, TIMESTAMP_END, TIMESTAMP_STEPS)):
            # String with signal value concatenated, per timestamp.
            timestamp_concat = None
            try:
                timestamp_concat = module_dict[timestamp]
            except KeyError:
                pass
            new_sig_value = get_value_signal_dict(signal_dict, timestamp)
            # Check if new_sig_value exists. if it exists, the value has changed.
            if new_sig_value is not None:
                # Signal changed, so change the current_sig_value.
                current_sig_value = new_sig_value

            # Concat this signal value to the total signals for this timestamp
            timestamp_concat = concat(timestamp_concat, current_sig_value)

            module_dict[timestamp] = timestamp_concat  
            
    # If method is tvla. We compute and store the hamming weight instead of the concatenated signal.
    if METHOD == "tvla":
        for timestamp in itertools.chain(range(TIMESTAMP_START, TIMESTAMP_END, TIMESTAMP_STEPS)):
            value = None
            try:
                value = module_dict[timestamp]
            except KeyError:
                pass
            if value is not None:
                module_dict[timestamp] = hamming_weight(conv_int(value))
            else:
                module_dict[timestamp] = 0
    return module_dict

# Starts 1 core process
# "file_path_queue" : Queue with file_paths.
# "modules" : List of string of module names.
def start_compute_sidechannel_traces(file_path_queue, modules):
    while not file_path_queue.empty():
        file_path = file_path_queue.get()
        vcd_file_name, vcd_file_extension = os.path.splitext(os.path.split(file_path)[1])
        vcd = open_VCD(file_path)
        if vcd is None:
            return
        for module in tqdm(modules, desc="Modules completed", leave=False):
            trace = compute_sidechannel_trace(vcd, module) # Computes the side-channel trace for this vcd file and module. 
            path = os.path.join(SIDECHANNEL_TRACES_PATH, module)
            write_file(path, vcd_file_name + ".json", trace) # Stores trace in a json file.
            
        # Manually delete vcd object to free memory.
        del vcd
        gc.collect()

# Computes side-channel traces.
# 'modules' : List of string of module names.
def compute_sidechannel_traces(modules):   
    file_path_queue = multiprocessing.Queue()
    for i in range(NR_OF_VCD_FILES):
        file_path = os.path.join(VCD_FILE_PATH, VCD_FILE_FORMAT.format(i)) 
        file_path_queue.put(file_path)
    
    processes = [multiprocessing.Process(target=start_compute_sidechannel_traces, args=(file_path_queue, modules,)) for x in range(NR_OF_CORES)]
    
    print("Starting processes.")
    for p in processes:
        p.start()
    
    # Waiting for processes.
    for p in processes:
        p.join()
    print("Processes finished.")

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
modules = ["TOP.mkTbSoc.soc_soc.ccore.riscv.stage3.multicycle_alu"]

for module in modules:
    path = os.path.join(SIDECHANNEL_TRACES_PATH, module)
    os.makedirs(path)
    
print("[INFO] VCD files: {}".format(NR_OF_VCD_FILES))
print("[INFO] VCD timestamps: from {} to {}".format(TIMESTAMP_START, TIMESTAMP_END))
print("[INFO] Number of cores: {}".format(NR_OF_CORES))
print("[INFO] Storing traces in directory: {}".format(SIDECHANNEL_TRACES_PATH))
print("[INFO] Accessing vcd files in directory: {}".format(VCD_FILE_PATH))
print("[INFO] Modules: {}".format(len(modules)))

# Compute side-channel traces.
compute_sidechannel_traces(modules)
store_config(config, config_file)