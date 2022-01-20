# PARAM

Techniques for exploring leaky components on a SoC

## Installation
Before we can compile the C-Class core, we have to install libraries for the core.  The following steps show how to install these required libraries.
Start by cloning our repository and its submodules with:
```bash
$ git clone --recurse-submodules https://github.com/nvandrueten/m_thesis.git
```
This will take a while, because this also clones the submodules which are quite large.


While it is cloning our repository, edit this to your liking and paste it into your `.bashrc`:
```bash
export PATH="/home/niels/.pyenv/bin:$PATH"
eval "$(pyenv init -)"
eval "$(pyenv virtualenv-init -)"
export RISCV="/home/niels/riscv/"
export PATH="$RISCV/bin:$PATH"
export SHAKTI_HOME="/home/niels/gitrepos/param/core/c-class"
```

Next, a lot of packages are needed for the project:
```bash
$ sudo apt-getinstall  -y  make  build-essential  libssl-dev  zlib1g-dev  libbz2-dev libreadline-dev libsqlite3-dev wget curl llvm libncurses5-dev libncursesw5-dev xz-utils tk-dev libffi-dev git ghc libghc-regex-compat-dev libghc-syb-dev libghc-old-time-dev libghc-split-dev  ghc-prof  libghc-regex-compat-prof  libghc-syb-proflibghc-old-time-prof  libghc-split-prof  gperf  autoconf  tcl-devflex  bison  iverilog  libtool  autoconf  automake  autotools-devcurl python3 libmpc-dev libmpfr-dev libgmp-dev gawk build-essential bison flex texinfo gperf libtool patchutils bc zlib1g-dev libexpat-dev swig python-dev texinfo python3-pip
```


### Python Environment
Install pyenv to create a virtual environment for Python
```bash
$ curl -L https://raw.githubusercontent.com/yyuu/pyenv-installer/master/bin/pyenv-installer | bash
```
Create a virtual environment with Python version 3.7.0 for our core,lets call the virtual environment:  ‘riscvenv’:
```bash
$ pyenv install 3.7.0
$ pyenv virtualenv 3.7.0 riscvenv
$ pyenv activate riscvenv
```
The  last  command  activates  the  riscvenv  virtual  environment.  Together with the PATH variables in your `.bashrc` file,  we can use use the last command.

### DTC
Now install DTC for RISC-V in the $RISCV directory:
```bash
$ cd core/dtc-1.4.7/
$ make NO_PYTHON=1 PREFIX=$RISCV
$ sudo make install NO_PYTHON=1 PREFIX=$RISCV
```

### BSC
We also need to install Blue Spec Compiler (BSC):
```bash
$ cd core/bsc/
$ make PREFIX=$RISCV
$ sudo make install PREFIX=$RISCV
```
The following command is optional and requires valgrind: `$sudo apt-getinstall valgrind`.
```
$ make check
```

### Verilator (Latest version)
Next, we install Verilator.  There is a Verilator package available with `$sudo apt-get install verilator', but this package is outdated and we need a newer version so we need to manually compile and install Verilator with Github repository:
```bash
$ git clone https://github.com/verilator/verilator
$ cd verilator
$ autoconf
$ ./configure
$ make 
$ sudo make install
```


### RISCV Openocd:
Now we install RISC-V OpenOCD:
```bash
$ cd core/riscv-openocd
$ ./bootstrap 
$ ./configure PREFIX=$RISCV
$ make PREFIX=$RISCV
$ sudo make install PREFIX=$RISCV
```

### RISCV GNU Toolchain:
This step will take some time where we install RISC-V GNU toolchain which installs the RISC-V compiler to compile C programs for a RISC-V processor:
```bash
$ cd core/riscv-gnu-toolchain
$ ./configure --prefix=$RISCV
$ sudo make
```

### RISCV-isa-sim + RISCV-isa-sim patch: 
The  last  thing  we  have  to  install  before  we  can  compile  the  c-class core, is a riscv-isa-sim modified for the C-Class core:
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
Now we are able to compile the C-Class core. First go to the c-class directory, activate the riscvenv Python virtual environment and install the required Python libraries with the following commands:
```bash
$ cd core/c-class
$ pyenv activate riscvenv
$ pip install -U -r requirements.txt
```

In the root directory of the git repository, we have a vcddump.yaml configuration file. This configuration file configures the C-Class core. Most configurations are default, but we have enabled the verilator configuration trace configuration flag to enable VCD dumps during simulation. With the following command, we configure the core with this configuration file:
```bash
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
