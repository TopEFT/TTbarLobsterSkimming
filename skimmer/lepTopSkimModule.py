# should be in CMSSW_10_6_19_patch2/src/PhysicsTools/NanoAODTools/python/postprocessing/modules/lepTop/

from PhysicsTools.NanoAODTools.postprocessing.framework.datamodel import Collection
from PhysicsTools.NanoAODTools.postprocessing.framework.eventloop import Module
import ROOT
ROOT.PyConfig.IgnoreCommandLineOptions = True


class lepTopSkimModule(Module):
    def __init__(self):
        self.el14Filt = lambda x: x.pt > 14
        self.el24Filt = lambda x: x.pt > 24
        self.mu14Filt = lambda x: x.pt > 14
        self.mu24Filt = lambda x: x.pt > 24

        pass

    def beginJob(self):
        pass

    def endJob(self):
        pass

    def beginFile(self, inputFile, outputFile, inputTree, wrappedOutputTree):
        self.out = wrappedOutputTree

    def endFile(self, inputFile, outputFile, inputTree, wrappedOutputTree):
        pass

    def analyze(self, event):
        """process event, return True (go to next module) or False (fail, go to next event)"""
        acceptEvent = False

        electrons = Collection(event, "Electron")
        muons = Collection(event, "Muon")

        ele14 = [x for x in filter(self.el14Filt, electrons)]
        ele24 = [x for x in filter(self.el24Filt, electrons)]
        mu14  = [x for x in filter(self.mu14Filt, muons)]
        mu24  = [x for x in filter(self.mu24Filt, muons)]

        nTotal14 = len(ele14) + len(mu14)   # number of leptons with pt>14
        nTotal24 = len(ele24) + len(mu24)   # number of leptons with pt>24

        if nTotal14 >= 2 and nTotal24 >= 1: 
            acceptEvent = True

        return acceptEvent

# define modules using the syntax 'name = lambda : constructor' to avoid having them loaded when not needed
lepTopSkimModuleConstr = lambda: lepTopSkimModule()
