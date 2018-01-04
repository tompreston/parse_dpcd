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
    0x000: DPCDReg("DP_DPCD_REV",
                   [DPCDData("major", 0xf, 4), DPCDData("minor", 0xf, 0)]),
    0x001: DPCDReg("MAX_LINK_RATE"),
    0x002: DPCDReg("MAX_LANE_COUNT",
                   [DPCDData("enhanced frame cap", 0x1, 7),
                    DPCDData("TPS3 supported", 0x1, 6),
                    DPCDData("max lanes", 0x1f, 0)]),
    0x003: DPCDReg("MAX_DOWNSPREAD"),
    0x004: DPCDReg("NORP & DP_PWR_VOLTAGE_CAP",
                   [DPCDData("18v_dp_pwr_cap", 0x1, 7),
                    DPCDData("12v_dp_pwr_cap", 0x1, 6),
                    DPCDData("5v_dp_pwr_cap", 0x1, 5),
                    DPCDData("#rx ports", 0xf, 0)]),
    0x005: DPCDReg("DOWNSTREAMPORT_PRESENT",
                   [DPCDData("dwn_strm_port_type", 0x2, 1),
                    DPCDData("dwn_strm_port_present", 0x1, 0)]),
    0x006: DPCDReg("MAIN_LINK_CHANNEL_CODING",
                   [DPCDData("ansi 8b/10b", 0x1, 0)]),
    0x007: DPCDReg("MAIN_LINK_CHANNEL_CODING",
                   [DPCDData("OUI Support", 0x1, 7),
                    DPCDData("msa_timing_par_ignored", 0x1, 6),
                    DPCDData("dwn_strm_port_count", 0xf, 0)]),
    0x008: DPCDReg("RECEIVE_PORT0_CAP_0",
                   [DPCDData("associated_to_preceding_port", 0x1, 2),
                    DPCDData("local_edid_present", 0x1, 1)]),
    0x009: DPCDReg("RECEIVE_PORT0_CAP_1",
                   [DPCDData("buffer_size", 0xff, 0)]),
    0x00a: DPCDReg("RECEIVE_PORT1_CAP_0",
                   [DPCDData("associated_to_preceding_port", 0x1, 2),
                    DPCDData("local_edid_present", 0x1, 1)]),
    0x00b: DPCDReg("RECEIVE_PORT1_CAP_1",
                   [DPCDData("buffer_size", 0xff, 0)]),
    0x00c: DPCDReg("I2C_SPEED_CONTROL"),
    0x00d: DPCDReg("eDP_CONFIGURATION_CAP",
                   [DPCDData("framing_change_capable", 0x1, 1),
                    DPCDData("alternate_scrambler_reset_capable", 0x1, 0)]),
    0x00e: DPCDReg("TRAINING_AUX_RD_INTERVAL"),
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
