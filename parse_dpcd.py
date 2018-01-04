"""
parse_dpcd.py - Parses DPCD data.
Usage:

    cat /sys/kernel/debug/dri/0/DP-1/i915_dpcd | python3 parse_dpcd.py

Copyright (C) 2017 Thomas Preston <thomasmarkpreston@gmail.com>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""
import collections
import fileinput
import logging

#logging.basicConfig(level=logging.DEBUG)

DPCDReg = collections.namedtuple("DPCDReg", ["name", "dpcd_data"])
DPCDData = collections.namedtuple("DPCDData", ["name", "mask", "shift"])

DPCD_REGS = {
    0x000: DPCDReg("DP_DPCD_REV",
                   [DPCDData("major", 0xf, 4), DPCDData("minor", 0xf, 0)]),
    0x001: DPCDReg("MAX_LINK_RATE", None),
    0x002: DPCDReg("MAX_LANE_COUNT",
                   [DPCDData("enhanced frame cap", 0x1, 7),
                    DPCDData("TPS3 supported", 0x1, 6),
                    DPCDData("max lanes", 0x1f, 0)]),
    0x003: DPCDReg("MAX_DOWNSPREAD", None),
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
    0x00c: DPCDReg("I2C_SPEED_CONTROL", None),
    0x00d: DPCDReg("eDP_CONFIGURATION_CAP",
                   [DPCDData("framing_change_capable", 0x1, 1),
                    DPCDData("alternate_scrambler_reset_capable", 0x1, 0)]),
    0x00e: DPCDReg("TRAINING_AUX_RD_INTERVAL", None),
    0x100: DPCDReg("LINK_BW_SET", None),
    0x101: DPCDReg("LANE_COUNT_SET",
                   [DPCDData("enhanced_frame_cap", 0x1, 7),
                    DPCDData("max_lane_count", 0xf, 0)]),
    0x102: DPCDReg("TRAINING_PATTERN_SET",
                   [DPCDData("scrambling_disable", 0x1, 5),
                    DPCDData("recovered_clock_out_en", 0x1, 4),
                    DPCDData("training_pattern_set", 0x3, 0)]),
    0x103: DPCDReg("TRAINING_LANE0_SET",
                   [DPCDData("max_pre-emphasis_reached", 0x1, 5),
                    DPCDData("pre-emphasis_set", 0x3, 3),
                    DPCDData("max_swing_reached", 0x1, 2),
                    DPCDData("voltage swing set", 0x3, 0)]),
    0x104: DPCDReg("TRAINING_LANE1_SET",
                   [DPCDData("max_pre-emphasis_reached", 0x1, 5),
                    DPCDData("pre-emphasis_set", 0x3, 3),
                    DPCDData("max_swing_reached", 0x1, 2),
                    DPCDData("voltage swing set", 0x3, 0)]),
    0x105: DPCDReg("TRAINING_LANE2_SET",
                   [DPCDData("max_pre-emphasis_reached", 0x1, 5),
                    DPCDData("pre-emphasis_set", 0x3, 3),
                    DPCDData("max_swing_reached", 0x1, 2),
                    DPCDData("voltage swing set", 0x3, 0)]),
    0x106: DPCDReg("TRAINING_LANE3_SET",
                   [DPCDData("max_pre-emphasis_reached", 0x1, 5),
                    DPCDData("pre-emphasis_set", 0x3, 3),
                    DPCDData("max_swing_reached", 0x1, 2),
                    DPCDData("voltage swing set", 0x3, 0)]),
    0x107: DPCDReg("DOWNSPREAD_CTRL",
                   [DPCDData("msa_timing_par_ignore_en", 0x1, 7),
                    DPCDData("spread_amp", 0x1, 4)]),
    0x108: DPCDReg("MAIN_LINK_CHANNEL_CODING_SET",
                   [DPCDData("set_ansi 8b10b", 0x1, 0)]),
    0x109: DPCDReg("I2C speed control/status", None),
    0x10a: DPCDReg("eDP_CONFIGURATION_SET",
                   [DPCDData("panel_self_test_enable", 0x1, 7),
                    DPCDData("framing_change_enable", 0x1, 1),
                    DPCDData("alternate_scramber_reset_enable", 0x1, 0)]),
}
MAX_LEN_REG_NAME = max(len(DPCD_REGS[addr].name) for addr in DPCD_REGS)

def reg_addr_str(name, addr):
    """Return a register name + address, right aligned."""
    return "{n:>{w}} {a:04x}".format(w=MAX_LEN_REG_NAME, n=name, a=addr)

def print_reg(addr, val):
    """Find a DPCD register in the DPCD_REGS map and print its value."""
    try:
        reg = DPCD_REGS[addr]
    except KeyError:
        print("{}: {:02x}".format(reg_addr_str("", addr), val))
        return

    if reg.dpcd_data:
        data = ["{}: {}".format(data.name, (val >> data.shift) & data.mask)
                for data in reg.dpcd_data]
        print("{}: {:02x}, {}".format(reg_addr_str(reg.name, addr), val,
                                      ", ".join(data)))
    else:
        print("{}: {:02x}".format(reg_addr_str(reg.name, addr), val))

def parse_dpcd_line(dpcd_line):
    """Parse a single DPCD line. Expected input:

        0000: 11 0a 84 01 01 00 01 80 02 00 00 00 00 00 00

    """
    logging.debug("parsing %s", dpcd_line)

    addr_str, regs_str = (s.strip() for s in dpcd_line.split(":"))
    addr_base = int(addr_str, 16)
    reg_vals = list(map(lambda h: int(h, 16), regs_str.split(" ")))

    for i, val in enumerate(reg_vals):
        print_reg(addr_base + i, val)

if __name__ == "__main__":
    for line in fileinput.input():
        line = line.strip()
        if line:
            parse_dpcd_line(line)
