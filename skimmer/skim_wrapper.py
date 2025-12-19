import subprocess
import sys
import os
import time
import argparse

parser = argparse.ArgumentParser(description='')
parser.add_argument('infiles', nargs='+', help='')
parser.add_argument('--cut','-c',type=str, help='')
parser.add_argument('--module','-m',type=str, help='')
parser.add_argument('--out-dir','-o',type=str,default='.', help='')

args = parser.parse_args()
skim_cut = args.cut
module   = args.module
out_dir  = args.out_dir
infiles  = args.infiles


REDIRECTOR = "root://cmsxrootd.crc.nd.edu/"
POSTFIX = "_Skim"

indent = " "*4*2

s = ["Current working directory:"]
for f in os.listdir('.'):
    s.append(indent + "{}".format(f))
print "\n".join(s)
print "\n\n Received infiles: {}\n\n".format(infiles)

local_files = []
for inf in infiles:
    local_name = inf.rsplit("/")[-1]

    if inf.startswith('/store'):
        remote_path = REDIRECTOR + inf
        ceph_path = "/cms/cephfs/data" + inf
    else:
        remote_path = inf.replace('file:', 'file://')
        ceph_path = None
    
    if local_name in os.listdir('.'):
        print "File {} already exists. Skipping xrdcp.".format(local_name)
        local_files.append(local_name)
        continue

    try:
        cmd_args = ['xrdcp', '-f', remote_path, local_name]
        print "Executing: {}".format(" ".join(cmd_args))
        subprocess.check_call(cmd_args)
        local_files.append(local_name)

    except subprocess.CalledProcessError:
        print "xrdcp failed for {}.".format(inf)
        if ceph_path and os.path.exists(ceph_path):
            print "Ceph path found! Using direct path: {}".format(ceph_path)
            local_files.append(ceph_path)
        else:
            print "Ceph mount not available or path wrong. Attempting remote streaming via XRootD..."
            local_files.append(remote_path)

s = "Sleeping..."
print s
time.sleep(10)

to_skim = local_files

cmd_args = ['nano_postproc.py']
cmd_args.extend(['-c','{}'.format(skim_cut)])
cmd_args.extend(['--postfix', POSTFIX])
# cmd_args.extend(['-I','CMGTools.TTHAnalysis.tools.nanoAOD.ttH_modules','lepJetBTagDeepFlav,{}'.format(module)])
cmd_args.extend([out_dir])
cmd_args.extend(to_skim)

s = "Skim command: {}".format(" ".join(cmd_args))
print s
subprocess.check_call(cmd_args)

to_merge = []
for path in to_skim:
    # Get the basename if it was a remote path
    base = path.rsplit("/")[-1]
    name_no_ext = base.replace(".root", "")
    expected_output = "{}{}.root".format(name_no_ext, POSTFIX)

    if os.path.exists(expected_output):
        to_merge.append(expected_output)
    else:
        print "Warning: Expected output {} not found!".format(expected_output)

if not to_merge:
    print "Error: No skimmed files found to merge. Check nano_postproc logs."
    sys.exit(1)

cmd_args = ['python', 'haddnano.py', 'output.root']
cmd_args.extend(to_merge)

print "\nMerge command: {}".format(" ".join(cmd_args))
subprocess.check_call(cmd_args)

print "\nProcessing complete. Final directory state:"
for f in os.listdir('.'):
    print "{}{}".format(indent, f)

