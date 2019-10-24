#!/usr/bin/env python3

# Emulate an arm system using uincorn with a binary produced by ghidra
# Given a pickle file as arg from Ghidra produced with `export_unicorn.py`,

# Usage: python3 import_unicorn.py pickle_file_path

(START,END) = (0x0, 0xFFFFFF)
DEBUG = False

import sys
import pickle

from unicorn import *
from unicorn.arm_const import *
from capstone import *

assert(len(sys.argv) > 1), f"USAGE: {sys.argv[0]} pickle_path"
in_path = sys.argv[1]

assert(os.path.isfile(sys.argv[1])), f"File {sys.argv[1]} not found"

with open(in_path, "rb") as f:
    data = pickle.load(f, encoding='utf8')

BAD_ADDRS = [] # Put addresses in here that you want to skip emulation of

def hook_code(emu, address, size, user_data):  
    global last_ib
    global idx
    #if DEBUG:
    codestr = ""
    if True:
        print('>>> Tracing instruction at 0x%x, instruction size = 0x%x' %(address, size))
        code = emu.mem_read(address, size)
        for i in disasm.disasm(code, size):
            codestr = ("\t0x{:x}\t{}\t{}".format(i.address, i.mnemonic, i.op_str))

    if address in BAD_ADDRS:
        emu.reg_write(UC_ARM_REG_PC, (address+size)|1)


# Initialize decompiler
disasm = Cs(CS_ARCH_ARM, CS_MODE_THUMB)
disasm.detail = True

# Initialize emulator and add hook callback
emu = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
emu.hook_add(UC_HOOK_CODE, hook_code)

# Map memory (TODO: differentiate RWX permissions?)
for (start,sz) in data["mem_regions"]:
    #print(f"Mapping from 0x{start:x} to 0x{start+sz:x}")
    emu.mem_map(start, sz)

# Set up data
for offset, raw_data in data["data"].items():
    #print(f"Filling in {len(raw_data)} bytes at 0x{offset:x}")
    emu.mem_write(offset, bytes(raw_data))

# Set up stack higher than all the functions we've mapped in already
stack_start = (max(e for (_, e) in data["mem_regions"])+0x10000) & ~0x1000
stack_size = 0x1000
emu.mem_map(stack_start, stack_size)

# Add a single argument to the stack and set up stack pointer
emu.mem_write(0x12345678, stack_start + 0x100)
emu.reg_write(UC_ARM_REG_SP, stack_start+0x100)

# Run emulator in thumb mode
emu.emu_start(START | 1, END)
