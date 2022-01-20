CC = gcc
CFLAGS = -g -O0 -static -Wall -Wextra #-Werror

RCC = riscv64-unknown-elf-gcc
RCFLAGS = -DPREALLOCATE=1 -mcmodel=medany -static -std=gnu99 -O0 -ffast-math -fno-common -fno-builtin-printf -static -nostdlib -nostartfiles -lm -lgcc -I/home/niels/gitrepos/param/core/c-class/verification/riscv-tests/env -I/home/niels/gitrepos/param/core/c-class/verification/riscv-tests/benchmarks/common -T/home/niels/gitrepos/param/core/c-class/verification/riscv-tests/benchmarks/common/test.ld

BUILDFILES = syscalls.c crt.S

# Where should the vcd files be stored:
VCD_PATH := /media/niels/Elements/research/vcd_files

# Location of RISC-V simulator
C_CLASS_BIN := /home/niels/gitrepos/param/core/c-class/bin


# Number of runs - 1
RUNS := 255

NUMBERS := $(shell seq 0 ${RUNS})
AESONLINEJOBS := $(addprefix aesjob,${NUMBERS})
AESOFFLINEJOBS := $(addprefix aesjot,${NUMBERS})
DESONLINEJOBS := $(addprefix desjob,${NUMBERS})
DESOFFLINEJOBS := $(addprefix desjot,${NUMBERS})
DES2ONLINEJOBS := $(addprefix des2job,${NUMBERS})
DES2OFFLINEJOBS := $(addprefix des2jot,${NUMBERS})
SHA3ONLINEJOBS := $(addprefix sha3job,${NUMBERS})
SHA3OFFLINEJOBS := $(addprefix sha3jot,${NUMBERS})

all: c riscv

aesonline.riscv: ${AESONLINEJOBS} ; echo "$@ success"
aesoffline.elf: ${AESOFFLINEJOBS} ; echo "$@ success"

desonline.riscv: ${DESONLINEJOBS} ; echo "$@ success"
desoffline.elf: ${DESOFFLINEJOBS} ; echo "$@ success"

des2online.riscv: ${DES2ONLINEJOBS} ; echo "$@ success"
des2offline.elf: ${DES2OFFLINEJOBS} ; echo "$@ success"

sha3online.riscv: ${SHA3ONLINEJOBS} ; echo "$@ success"
sha3offline.elf: ${SHA3OFFLINEJOBS} ; echo "$@ success"

${AESONLINEJOBS}: aesjob%: ; $(RCC) $(RCFLAGS) -DSVF -DRUN=$* -DFIRSTROUNDONLY syscalls.c crt.S aes.c -o aes.riscv;
		elf2hex 8 4194304 aes.riscv 2147483648 > aes.riscv.hex
		cp aes.riscv.hex $(C_CLASS_BIN)/code.mem
		cd $(C_CLASS_BIN) && ./out +trace
		cp $(C_CLASS_BIN)/logs/vlt_dump.vcd $(VCD_PATH)/aes/round_$*.vcd
		rm aes.riscv

${AESOFFLINEJOBS}: aesjot%: ; $(CC) $(CFLAGS) -DOFFLINE -DSVF -DRUN=$* -DFIRSTROUNDONLY aes.c -o aesoffline.elf
		./aesoffline.elf
		rm aesoffline.elf

${DESONLINEJOBS}: desjob%: ; $(RCC) $(RCFLAGS) -DSVF -DRUN=$* -DFIRSTROUNDONLY syscalls.c crt.S des.c -o des.riscv;
		elf2hex 8 4194304 des.riscv 2147483648 > des.riscv.hex
		cp des.riscv.hex $(C_CLASS_BIN)/code.mem
		cd $(C_CLASS_BIN) && ./out +trace
		cp $(C_CLASS_BIN)/logs/vlt_dump.vcd $(VCD_PATH)/des/round_$*.vcd
		rm des.riscv

${DESOFFLINEJOBS}: desjot%: ; $(CC) $(CFLAGS) -DOFFLINE -DSVF -DRUN=$* -DFIRSTROUNDONLY des.c -o desoffline.elf
		./desoffline.elf
		rm desoffline.elf

${DES2ONLINEJOBS}: des2job%: ; $(RCC) $(RCFLAGS) -DSVF -DRUN=$* -DFIRSTROUNDONLY syscalls.c crt.S des2.c -o des2.riscv;
		elf2hex 8 4194304 des2.riscv 2147483648 > des2.riscv.hex
		cp des2.riscv.hex $(C_CLASS_BIN)/code.mem
		cd $(C_CLASS_BIN) && ./out +trace
		cp $(C_CLASS_BIN)/logs/vlt_dump.vcd $(VCD_PATH)/des2/round_$*.vcd
		rm des2.riscv

${DES2OFFLINEJOBS}: des2jot%: ; $(CC) $(CFLAGS) -DOFFLINE -DSVF -DRUN=$* -DFIRSTROUNDONLY des2.c -o des2offline.elf
		./des2offline.elf
		rm des2offline.elf

${SHA3ONLINEJOBS}: sha3job%: ; $(RCC) $(RCFLAGS) -DSVF -DRUN=$* -DFIRSTROUNDONLY syscalls.c crt.S sha3.c sha3_imp.c -o sha3.riscv;
		elf2hex 8 4194304 sha3.riscv 2147483648 > sha3.riscv.hex
		cp sha3.riscv.hex $(C_CLASS_BIN)/code.mem
		cd $(C_CLASS_BIN) && ./out +trace
		cp $(C_CLASS_BIN)/logs/vlt_dump.vcd $(VCD_PATH)/sha3/round_$*.vcd
		rm sha3.riscv

${SHA3OFFLINEJOBS}: sha3jot%: ; $(CC) $(CFLAGS) -DOFFLINE -DSVF -DRUN=$* -DFIRSTROUNDONLY sha3.c sha3_imp.c -o sha3offline.elf
		./sha3offline.elf
		rm sha3offline.elf

c: aes.elf des.elf des2.elf sha3.elf

riscv: aes.riscv des.riscv des2.riscv sha3.riscv

# AES compilation options.
aes.elf: aes.c
	$(CC) $(CFLAGS) -DOFFLINE -DSVF $^ -o $@

aes1round.elf: aes.c
	$(CC) $(CFLAGS) -DOFFLINE -DSVF -DFIRSTROUNDONLY  $^ -o $@

aes.riscv: $(BUILDFILES) aes.c
	$(RCC) $(RCFLAGS) -DSVF -DRUN=1 $^ -o $@
	riscv64-unknown-elf-objdump --disassemble-all --disassemble-zeroes --section=.text --section=.text.startup --section=.data $@ > $@.dump
	elf2hex 8 4194304 $@ 2147483648 > $@.hex

# DES compilation options.
des.elf: des.c
	$(CC) $(CFLAGS) -DOFFLINE -DSVF $^ -o $@

des1round.elf: des.c
	$(CC) $(CFLAGS) -DOFFLINE -DSVF -DFIRSTROUNDONLY $^ -o $@

des.riscv: $(BUILDFILES) des.c
	$(RCC) $(RCFLAGS) -DSVF -DRUN=1 $^ -o $@
	riscv64-unknown-elf-objdump --disassemble-all --disassemble-zeroes --section=.text --section=.text.startup --section=.data $@ > $@.dump
	elf2hex 8 4194304 $@ 2147483648 > $@.hex

# DES2 compilation options.
des2.elf: des2.c
	$(CC) $(CFLAGS) -DOFFLINE -DSVF $^ -o $@

des21round.elf: des2.c
	$(CC) $(CFLAGS) -DOFFLINE -DSVF -DFIRSTROUNDONLY $^ -o $@

des2.riscv: $(BUILDFILES) des2.c
	$(RCC) $(RCFLAGS) -DSVF -DRUN=1 $^ -o $@
	riscv64-unknown-elf-objdump --disassemble-all --disassemble-zeroes --section=.text --section=.text.startup --section=.data $@ > $@.dump
	elf2hex 8 4194304 $@ 2147483648 > $@.hex


# SHA-3 compilation options.
sha3.elf: sha3.c sha3_imp.c
	$(CC) $(CFLAGS) -DOFFLINE -DSVF $^ -o $@

sha31round.elf: sha3.c sha3_imp.c
	$(CC) $(CFLAGS) -DOFFLINE -DSVF -DFIRSTROUNDONLY $^ -o $@

sha3.riscv: $(BUILDFILES) sha3.c sha3_imp.c
	$(RCC) $(RCFLAGS) -DSVF -DRUN=1 $^ -o $@
	riscv64-unknown-elf-objdump --disassemble-all --disassemble-zeroes --section=.text --section=.text.startup --section=.data $@ > $@.dump
	elf2hex 8 4194304 $@ 2147483648 > $@.hex


# TVLA compilation options.
aes_tvlafixed.riscv: $(BUILDFILES) aes.c
	$(RCC) $(RCFLAGS) -DTVLA_FIXED -DFIRSTROUNDONLY syscalls.c crt.S aes.c -o $@;
	elf2hex 8 4194304 $@ 2147483648 > $@.hex
	cp $@.hex $(C_CLASS_BIN)/code.mem
	cd $(C_CLASS_BIN) && ./out +trace
	cp $(C_CLASS_BIN)/logs/vlt_dump.vcd $(VCD_PATH)/aes/tvla_fixed/round_0.vcd
	rm $@

des_tvlafixed.riscv: $(BUILDFILES) des.c
	$(RCC) $(RCFLAGS) -DTVLA_FIXED -DFIRSTROUNDONLY syscalls.c crt.S des.c -o $@;
	elf2hex 8 4194304 $@ 2147483648 > $@.hex
	cp $@.hex $(C_CLASS_BIN)/code.mem
	cd $(C_CLASS_BIN) && ./out +trace
	cp $(C_CLASS_BIN)/logs/vlt_dump.vcd $(VCD_PATH)/des/tvla_fixed/round_0.vcd
	rm $@

des2_tvlafixed.riscv: $(BUILDFILES) des2.c
	$(RCC) $(RCFLAGS) -DTVLA_FIXED -DFIRSTROUNDONLY syscalls.c crt.S des2.c -o $@;
	elf2hex 8 4194304 $@ 2147483648 > $@.hex
	cp $@.hex $(C_CLASS_BIN)/code.mem
	cd $(C_CLASS_BIN) && ./out +trace
	cp $(C_CLASS_BIN)/logs/vlt_dump.vcd $(VCD_PATH)/des2/tvla_fixed/round_0.vcd
	rm $@

sha3_tvlafixed.riscv: $(BUILDFILES) sha3.c sha3_imp.c
	$(RCC) $(RCFLAGS) -DTVLA_FIXED -DFIRSTROUNDONLY syscalls.c crt.S sha3.c sha3_imp.c -o $@;
	elf2hex 8 4194304 $@ 2147483648 > $@.hex
	cp $@.hex $(C_CLASS_BIN)/code.mem
	cd $(C_CLASS_BIN) && ./out +trace
	cp $(C_CLASS_BIN)/logs/vlt_dump.vcd $(VCD_PATH)/sha3/tvla_fixed/round_0.vcd
	rm $@

run: c
	./aes.elf
	./des.elf

clean:
	rm -rf *.riscv *.elf *.txt *.hex *.dump
