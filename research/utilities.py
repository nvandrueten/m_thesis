from tqdm import trange, tqdm # if not running in a notebook

def find_tv_value(signal_tvs, timestamp):
    for i in range(len(signal_tvs)):
        timestamp_, sig_value = signal_tvs[i]
        if timestamp_ == timestamp:
            return i
    return None

# Returns a list of modules name
def get_modules_names_list(vcd):
    modules = vcd.scopes
    module_dict = dict()
    modlist = list(modules)
    return modlist

# Checks whether 'module_name' is in the list of 'modules'
def find_module(modules, module_name):
    return module_name in modules

# Returns module object from module string
def get_module_object(vcd, module_name):
    modules = vcd.scopes
    return modules[module_name]

# Function to access all signals for a module
def signal_access(vcd, module_name):
    module_object = get_module_object(vcd, module_name)
    modules_name_list = get_modules_names_list(vcd)
    # .subElements returns signals and submodules of this module.
    # We are only interested in the signals, since the submodules are 
    # analysed independently.
    # Only store signals in signal_list.
    signals = module_object.subElements
    signal_list = []
    for signal in signals:
        signame = module_name + "." + signal
        if not find_module(modules_name_list, signame):
            sigvalue = vcd[signame]
            signal_list.append(sigvalue)
    return signal_list

def fst(_tuple):
    return _tuple[0]

def snd(_tuple):
    return _tuple[1]

# VCDVCD library stores values as str with base 8: 6 => '110'
# This function translates '110' to 6.
def conv_int(string):
    return int(string, 2)

def strip_bin(x):
    return x[2:]

# Concat x and y, while taking account both variables could be None.
def concat(x, y):
    if x is None and y is None: 
        return None
    if x is None:
        return y
    if y is None:
        return x
    else:
        return x + y
    
def get_signal_dict(tv):
    return dict(tv)

def get_value_signal_dict(tv_dict, timestamp):
    return tv_dict.get(timestamp)

# Splits list in num-sized lists.
# Used for multi-core run to
# distribute the modules.
def chunkIt(seq, num):
    avg = len(seq) / float(num)
    out = []
    last = 0.0

    while last < len(seq):
        out.append(seq[int(last):int(last + avg)])
        last += avg

    return out

