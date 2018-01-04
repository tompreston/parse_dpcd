"""
parse_dpcd.py - Parses DPCD data.
Author: Thomas Preston

Usage:

        cat /sys/kernel/debug/dri/0/DP-1/i915_dpcd | python3 parse_dpcd.py

"""
import fileinput
import logging

logging.basicConfig(level=logging.DEBUG)

class DPCDReg():
    def __init__(self, name, dpcd_data=None):
        self.name = name
        self.dpcd_data = dpcd_data

class DPCDData():
    def __init__(self, name, mask, shift):
        self.name = name
        self.mask = mask
        self.shift = shift

DPCD_REGS = {
    0x000: DPCDReg("DP_DPCD_REV", [DPCDData("major", 0xf, 4),
                                   DPCDData("minor", 0xf, 0)]),
    0x001: DPCDReg("MAX_LINK_RATE"),
}

def reg_addr_str(name, addr):
    return "{:>20} {:04x}".format(name, addr)

def print_reg(addr, val):
    try:
        reg = DPCD_REGS[addr]
    except KeyError:
        print("{:>25}: {:02x}".format(reg_addr_str("", addr), val))
        return

    if reg.dpcd_data:
        data = ["{}: {}".format(data.name, (val >> data.shift) & data.mask)
                for data in reg.dpcd_data]
        print("{:>25}: {:02x}, {}".format(reg_addr_str(reg.name, addr), val,
                                          ", ".join(data)))
    else:
        print("{:>25}: {:02x}".format(reg_addr_str(reg.name, addr), val))

def parse_dpcd_line(line):
    logging.debug("parsing %s", line)

    addr_str, regs_str = (s.strip() for s in line.split(":"))
    addr_base = int(addr_str, 16)
    reg_vals = list(map(lambda h: int(h, 16), regs_str.split(" ")))

    for i, val in enumerate(reg_vals):
        print_reg(addr_base + i, val)

if __name__ == "__main__":
    for line in fileinput.input():
        line = line.strip()
        if line:
            parse_dpcd_line(line)
