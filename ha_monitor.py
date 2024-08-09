#! /usr/bin/env python
import subprocess
import os
import time
from datetime import datetime

#monitor ha_agent for intermittent HA issues trigger a tcpdump
#root access required
#tested in 11.1
#adjust peer ip

log_file = "/var/log/pan/ha_agent.log"
search_string = "ping timeouts out of 3"
check_interval = 1
peer_ip = "10.194.80.107"

def run_tcpdump():
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    tcpdump_output = f"/opt/pancfg/mgmt/saved-configs/ha_mon_{timestamp}.pcap"
    cmd = ["timeout", "10", "tcpdump", "-i", "eth0", "icmp and host", peer_ip, "-w", tcpdump_output] #use timeout to overcome tcpdump bug that doesn't adhere to value set on -C
    print(f"Running tcpdump: {' '.join(cmd)}")
    subprocess.run(cmd)
    print(f"tcpdump finished, output saved to {tcpdump_output}")

def tail_and_trigger(log_file, search_string):
    with open(log_file, "r") as f:
        # Move to the end of the file
        f.seek(0, os.SEEK_END)

        try:
            while True:
                line = f.readline()
                if not line:
                    time.sleep(check_interval)
                    continue
                if search_string in line:
                    run_tcpdump()
                if "HA1 connection down" in line:
                    run_tcpdump()
                    exit()
        except KeyboardInterrupt:
            print("Stopping monitoring.")

if __name__ == "__main__":
    tail_and_trigger(log_file, search_string)
