# DPCD parser
Parse DisplayPort Configuration Data

Example usage:

    cat /sys/kernel/debug/dri/0/DP-1/i915_dpcd | python3 parse_dpcd.py --data
    python3 parse_dpcd.py --help

