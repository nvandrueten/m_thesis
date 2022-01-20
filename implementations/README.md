## Implementations
This directory contains c programs with compile options to compile on the c-class core.

NOTE: Files `syscalls.c` and `crt.S` are made by c-class developers and are used to compile successfully.

### How to compile
#### Cleaning implementations/ directory:
``
$ make clean
``
#### AES online runs:
``
$ make aesonline.riscv RUNS=<number of runs - 1> VCD_PATH=<destination path for vcd files> C_CLASS_BIN=<path of C-Class bin directory>
``
#### DES online runs:
``
$ make desonline.riscv RUNS=<number of runs - 1> VCD_PATH=<destination path for vcd files> C_CLASS_BIN=<path of C-Class bin directory>
``
#### AES offline runs:
``
$ make aesoffline.elf RUNS=<number of runs>
``
#### DES offline runs:
``
$ make desoffline.elf RUNS=<number of runs>
``
