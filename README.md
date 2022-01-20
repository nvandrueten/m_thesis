# PARAM

Techniques for exploring leaky components on a SoC

## Installation
Clone this repository and its submodules:
```bash
$ git clone --recurse-submodules https://gitlab.science.ru.nl/kmiteloudi/param.git
```

Edit this and add to your `.bashrc`:
```bash
export PATH="/home/niels/.pyenv/bin:$PATH"
eval "$(pyenv init -)"
eval "$(pyenv virtualenv-init -)"
export RISCV="/home/niels/riscv/"
export PATH="$RISCV/bin:$PATH"
export SHAKTI_HOME="/home/niels/gitrepos/param/core/c-class"
```

### Python Environment
```bash
$ sudo apt-get install -y make build-essential libssl-dev zlib1g-dev libbz2-dev \
    libreadline-dev libsqlite3-dev wget curl llvm libncurses5-dev libncursesw5-dev \
    xz-utils tk-dev libffi-dev liblzma-dev python-openssl git
$ curl -L https://raw.githubusercontent.com/yyuu/pyenv-installer/master/bin/pyenv-installer | bash

$ pyenv install 3.7.0
$ pyenv virtualenv 3.7.0 riscvenv
```

### DTC
```bash
$ sudo apt-get install flex bison
$ cd core/dtc-1.4.7/
$ make NO_PYTHON=1 PREFIX=$RISCV
$ sudo make install NO_PYTHON=1 PREFIX=$RISCV
```

### BSC
```bash
$ cd core/bsc/
$ sudo apt-get install ghc libghc-regex-compat-dev libghc-syb-dev libghc-old-time-dev libghc-split-dev ghc-prof libghc-regex-compat-prof libghc-syb-prof libghc-old-time-prof libghc-split-prof gperf autoconf tcl-dev flex bison iverilog
$ make PREFIX=$RISCV
$ sudo make install PREFIX=$RISCV
$ make check
```

### Verilator (Latest version)
```bash
$ git clone https://github.com/verilator/verilator
$ cd verilator
$ autoconf
$ ./configure
$ make 
$ sudo make install
```


### RISCV Openocd:
```bash
$ sudo apt-get install libtool
$ cd core/riscv-openocd
$ ./bootstrap 
$ ./configure PREFIX=$RISCV
$ make PREFIX=$RISCV
$ sudo make install PREFIX=$RISCV
```

### RISCV GNU Toolchain:
```bash
$ cd core/riscv-gnu-toolchain
$ sudo apt-get install autoconf automake autotools-dev curl python3 libmpc-dev libmpfr-dev libgmp-dev gawk build-essential bison flex texinfo gperf libtool patchutils bc zlib1g-dev libexpat-dev
$ ./configure --prefix=$RISCV
$ sudo make
```

### RISCV-isa-sim + RISCV-isa-sim patch: 
```bash
$ cd core/mod-spike                                 
$ git checkout bump-to-latest       
$ cd core/riscv-isa-sim
$ git checkout 6d15c93fd75db322981fe58ea1db13035e0f7add
$ git apply ../mod-spike/shakti.patch
$ mkdir build
$ cd build
$ ../configure --prefix=$RISCV
$ make
$ sudo make install
```

## Build C-Class core
```bash
$ cd core/c-class
$ pyenv activate riscvenv
$ pip install -U -r requirements.txt
$ python -m configure.main -ispec sample_config/default.yaml
```

Edit line in `core/c-class/verification/riscv-tests/env/v/vm.c`: 
- `volatile uint64_t tohost;` => `extern volatile uint64_t tohost;`
- `volatile uint64_t fromhost;` => `extern volatile uint64_t fromhost;`

Create `soc_config.inc` file in `core/c-class` with:
```
ISA=RV64IMAFD
MMU=enable
AXI=enable
BPU=enable
MUL=sequential
PERF=enable
VERBOSE=disable
PREFETCH=enable
DEBUG=disable
OPENOCD=disable
QSPI0=disable
QSPI1=disable
SDRAM=disable
UART0=enable
UART1=enable
PLIC=disable
BOOTROM=enable
I2C0=disable
I2C1=disable
DMA=disable
AXIEXP=disable
TCM=disable
CLINT=disable
SYNTH=SIM
FLASHMODEL=cypress
```

```bash
$ make default
```
This creates a bin folder with a out executable. 

## Regression tests C-Class core
Do one test:
```bash
$ make test opts='--test=add --suite=rv64ui' CONFIG_ISA=RV64IMAFDC
```

To view debug information, such as executed commands in the regression test, add `--debug` to the opts string:
```bash
$ make test opts='--test=add --suite=rv64ui --debug' CONFIG_ISA=RV64IMAFDC
```

Start regression tests:
```bash
$ make regress opts='--filter=rv64 --parallel=7 --sub' CONFIG_ISA=RV64IMAFDC
$ make regress opts='--filter=rv64 --final'
```


## Run program on core
The core executable is located in bin/out. This executable requires a program compiled with the riscv-gcc compiler. This compiled program must be translated to hex, placed in the same directory as the core and named as code.mem.

### Compile a C program
To compile a c program, three steps are required: (1) Compile with riscv-v compiler, (2), translate risc-v executable to a hex file, (3) Place hex file near core executable. There is a makefile in the implementations directory that compiles c programs with a riscv compiler and translate the risc-v compiler to a hex file. 

### Run compiled C program on core 
The hex file should be placed in the same directory as the out executable of the c-class. It has to be renamed to `code.mem`. Once you have the code.mem file, you can start the core with
```
./out
```

Some flags are useful during simulation.
 - +rtldump: Creates a dump file with a list of executed instructions. The file has the following format: `<privilege-mode> <program-counter> <instruction> <register-updated><register value>`. 
 - +trace. Creates a .vcd dump file to view signal values in a waveviewer. This flag only works when the core has been configured with the `trace_dump` enabled.
 
 ## Research
 
 ### Python requirements
 - vcdvcd numpy scipy tqdm matplotlib
 
 ### Configuration file
 File `config.ini.example` contains the configuration settings, such as file locations and nr of core used, for our research. Copy this file to `config.ini` and edit the settings for your environment.
 
 
 ### Compute vcd timestamp end
 `$ python getvcdlength.py` computes the last timestamp of the vcd file targeted. Required in config file.
 ### Compute traces
 `$ python compute_traces.py` computes the side-channel traces.
 
 ### Compute HDs
 `$ python compute_hd.py` computes the hamming distance values for svf.
 
 ### Compute SVF
 `$ python svf.py` computes svf values per module. Requires a run of compute_traces.py and compute_hd.py with METHOD = svf. 

 ### Compute TVLA
 `$ python tvla.py` computes tvla. Requires a run of compute_traces with METHOD = tvla and TVLA_FIXED = yes to compute traces for fixed set. Requires a run of compute_traces with METHOD = tvla and TVLA_FIXED = no to compute traces for random set. 
