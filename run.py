#!/usr/bin/env python3
from datetime import datetime
from os import makedirs
from os.path import isdir, isfile
from subprocess import call
from sys import argv, stdout
import argparse

# useful constants
VERSION = '0.0.1'
LOGFILE = None

# check if user is just printing version
if '--version' in argv:
    print("FAVITES-COVID-Lite version %s" % VERSION); exit()

# return the current time as a string
def get_time():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# print to the log (None implies stdout only)
def print_log(s='', end='\n'):
    tmp = "[%s] %s" % (get_time(), s)
    print(tmp, end=end); stdout.flush()
    if LOGFILE is not None:
        print(tmp, file=LOGFILE, end=end); LOGFILE.flush()

# parse user args
def parse_args():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('-o', '--output', required=True, type=str, help="Output Directory")
    parser.add_argument('--path_ngg_barabasi_albert', required=False, type=str, default='ngg_barabasi_albert', help="Path to 'ngg_barabasi_albert' executable")
    parser.add_argument('--cn_n', required=True, type=int, help="Contact Network: BA model n (number of nodes)")
    parser.add_argument('--cn_m', required=True, type=int, help="Contact Network: BA model m (number of edges from new node)")
    parser.add_argument('--gzip_output', action='store_true', help="Gzip Compress Output Files")
    parser.add_argument('--version', action='store_true', help="Display Version")
    return parser.parse_args()

# simulate contact network under BA model
def simulate_contact_network_ba(n, m, out_fn, path_ngg_barabasi_albert):
    print_log("Contact Network Model: Barabasi-Albert (BA)")
    print_log("BA n Parameter: %d" % n)
    print_log("BA m Parameter: %d" % m)
    command = [path_ngg_barabasi_albert, str(n), str(m)]
    print_log("NiemaGraphGen Command: %s" % ' '.join(command))
    out_file = open(out_fn, 'w')
    if call(command, stdout=out_file) != 0:
        raise RuntimeError("Error when running: %s" % path_ngg_barabasi_albert)
    out_file.close()
    print_log("Contact Network simulation complete: %s" % out_fn)

# main execution
if __name__ == "__main__":
    # parse and check user args
    args = parse_args()
    if isdir(args.output) or isfile(args.output):
        raise ValueError("Output directory exists: %s" % args.output)
    if args.cn_n < args.cn_m:
        raise ValueError("In the BA model, the number of nodes (%d) must be larger than the number of edges from new nodes (%d)" % (args.cn_n, args.cn_m))

    # set up output directory
    makedirs(args.output, exist_ok=True)
    LOGFILE_fn = "%s/log.txt" % args.output
    LOGFILE = open(LOGFILE_fn, 'w')

    # print run info to log
    print_log("===== RUN INFORMATION =====")
    print_log("FAVITES-COVID-Lite Version: %s" % VERSION)
    print_log("FAVITES-COVID-Lite Command: %s" % ' '.join(argv))
    print_log("Output Directory: %s" % args.output)
    print_log()

    # simulate contact network
    cn_fn = "%s/contact_network.txt" % args.output
    print_log("===== CONTACT NETWORK =====")
    simulate_contact_network_ba(args.cn_n, args.cn_m, cn_fn, args.path_ngg_barabasi_albert)
    print_log()

    # gzip output files (if requested)
    if args.gzip_output:
        print_log("===== GZIP OUTPUT FILES =====")
        fns_to_compress = [cn_fn]
        for fn in fns_to_compress:
            command = ['gzip', '-9', fn]
            if call(command) != 0:
                raise RuntimeError("Failed to gzip: %s" % fn)
            print_log("Successfully compressed: %s" % fn)

    # clean things up
    LOGFILE.close()
