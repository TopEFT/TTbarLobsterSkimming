import datetime
import os
import sys
import shutil
import subprocess
from os import path
from lobster import cmssw
from lobster.core import AdvancedOptions, Category, Config, Dataset, ParentDataset, StorageConfiguration, Workflow

timestamp_tag = datetime.datetime.now().strftime('%Y%m%d_%H%M')

sys.path.append(os.path.split(__file__)[0])
from tools.utils import read_cfg


sandbox_location = "/users/hnelson2/TTbarLobsterSkimming/skimmer/CMSSW_10_6_19_patch2/"
hadd_path = os.path.join(sandbox_location, 'src/PhysicsTools/NanoAODTools/scripts/haddnano.py')

cfg_fpath = "/users/hnelson2/TTbarLobsterSkimming/samples/"


# # used this for the full ptSkimming of run2, just an issue with one file
# # outdir: /store/user/$USER/skims/{tag}/{ver}
# cfg_name = "data_samples.cfg"
# tag = "data/FullRun2"
# ver = "ptSkim"
# match = ['.*\\.json']

# # outdir: /store/user/$USER/skims/{tag}/{ver}
# cfg_name = "mc_DY_samples.cfg"
# tag = "mc/ptSkim"
# ver = "DY"
# match = ['.*\\.json']

# outdir: /store/user/$USER/skims/{tag}/{ver}
# cfg_name = "mc_background_samples.cfg"
# tag = "mc/ptSkim"
# ver = "background"
# match = ['.*\\.json']

# # outdir: /store/user/$USER/skims/{tag}/{ver}
# cfg_name = "mc_signal_samples.cfg"
# tag = "mc/ptSkim"
# ver = "PowhegTTto2L2Nu"
# match = ['.*\\.json']

# outdir: /store/user/$USER/skims/{tag}/{ver}
cfg_name = "mc_tW_samples.cfg"
tag = "mc/ptSkim"
ver = "tW_NoFullyHadronicDecays"
match = ['.*\\.json']

master_label = 'T3_EFT_{tstamp}'.format(tstamp=timestamp_tag)
output_path  = "/store/user/$USER/skims/{tag}/{ver}".format(tag=tag, ver=ver)
workdir_path = "/tmpscratch/users/$USER/skims/{tag}/{ver}".format(tag=tag, ver=ver)
plotdir_path = "~/afs/www/lobster/skims/{tag}/{ver}".format(tag=tag, ver=ver)

# Different xrd src redirectors depending on where the inputs are stored

storage = StorageConfiguration(
    input = [
        "file:///cms/cephfs/data/",
        "root://cmsxrootd.crc.nd.edu/",
    ],
    
    output=[
        "file:///cms/cephfs/data" + output_path,
        "root://cmsxrootd.crc.nd.edu/"+output_path,    
    ],
)

# See tools/utils.py for dict structure of returned object
cfg = read_cfg(os.path.join(cfg_fpath, cfg_name),match=match)

cat = Category(
    name='processing',
    cores=1,
    memory=4000,
    disk=10000,
)

wf = []
for sample in sorted(cfg['jsons']):
    jsn = cfg['jsons'][sample]
    print(f"Sample: {sample}")
    files = jsn['files']
    # for fn in jsn['files']:
    #     print "\t{}".format(fn)
    # files = [x.replace('/store/','') for x in jsn['files']]

    ds_base = Dataset(
        files=files,
        files_per_task=1
    )

    # ds_cmssw = cmssw.Dataset(
    #     dataset=jsn['path'],
    #     lumis_per_task=1,   # Since file_based is true, this will be files_per_task
    #     file_based=True
    # )

    # ds = ds_cmssw         # used to run over Data
    ds = ds_base

    cmd = ['python','skim_wrapper.py']
    # skim_cut = "'nMuon+nElectron >=2'"
    # cmd.extend(['--cut',skim_cut]) # use this with the above line skim_cut instead of the module
    cmd.extend(['--module', 'lepTopSkimModule'])
    cmd.extend(['--out-dir','.'])
    cmd.extend(['@inputfiles'])
    skim_wf = Workflow(
        label=sample.replace('-','_'),
        sandbox=cmssw.Sandbox(release=sandbox_location),
        dataset=ds,
        category=cat,
        extra_inputs=['skim_wrapper.py',hadd_path],
        outputs=['output.root'],
        command=' '.join(cmd),
        merge_command='python haddnano.py @outputfiles @inputfiles',
        merge_size='537M',
        globaltag=False,    # To avoid autosense crash (can be anything, just not None)
        cleanup_input=False
    )
    wf.extend([skim_wf])

config = Config(
    label=master_label,
    workdir=workdir_path,
    plotdir=plotdir_path,
    storage=storage,
    workflows=wf,
    advanced=AdvancedOptions(
        # dashboard=False, # Important to avoid a crash caused by out of date WMCore
        bad_exit_codes=[127, 160],
        log_level=1,
        payload=10,
        osg_version='3.6',
        # xrootd_servers=[
        #     'ndcms.crc.nd.edu',
        #     # 'cmsxrootd.fnal.gov',
        #     # 'deepthought.crc.nd.edu'
        # ]
    )
)
