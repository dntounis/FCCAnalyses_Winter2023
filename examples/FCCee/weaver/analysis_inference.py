import os
import urllib.request

# ____________________________________________________________
def get_file_path(url, filename):
    if os.path.exists(filename):
        return os.path.abspath(filename)
    else:
        urllib.request.urlretrieve(url, os.path.basename(url))
        return os.path.basename(url)

# ____________________________________________________________

## input file needed for unit test in CI
testFile = "https://fccsw.web.cern.ch/fccsw/testsamples/wzp6_ee_nunuH_Hss_ecm240.root"

## output directory
#outputDir   = "outputs/inference"
outputDir = "./" #Jim

## latest particle transformer model, trainied on 9M jets in winter2023 samples
#model_name = "fccee_flavtagging_edm4hep_wc_v1"
#model_name = "PNet_Hss_test_v1" #Jim
#model_name="PNet_Hss_SiD_o2_vo4_Winter2023_C_27epochs"

#production Oct 2024
#model_name="PNet_Hss_SiD_o2_v04_C_4Oct24_best_epoch_state"
model_name="PNet_Hss_IDEA_4Oct24_best_epoch_state"
#model_name="PNet_Hss_SiD_o2_v04_D_4Oct24_best_epoch_state"


## model files needed for unit testing in CI
url_model_dir = "https://fccsw.web.cern.ch/fccsw/testsamples/jet_flavour_tagging/winter2023/wc_pt_13_01_2022/"
url_preproc = "{}/{}.json".format(url_model_dir, model_name)
url_model = "{}/{}.onnx".format(url_model_dir, model_name)

## model files locally stored on /eos
#model_dir = "/fs/ddn/sdf/group/atlas/d/dntounis/Hss/weaver_training/particle_transformer/models/"

#production Oct 2024
model_dir = "/fs/ddn/sdf/group/atlas/d/dntounis/Hss/weaver_training/models_productionOct2024/ONNX_models"


local_preproc = "{}/{}.json".format(model_dir, model_name)
local_model = "{}/{}.onnx".format(model_dir, model_name)

## get local file, else download from url
weaver_preproc = get_file_path(url_preproc, local_preproc)
weaver_model = get_file_path(url_model, local_model)

#import sys
#Jim
#sys.path.insert(0,'/home/dntounis/Hss_setup_test/FCCAnalyses_Winter2023')

#from addons.ONNXRuntime.jetFlavourHelper import JetFlavourHelper
#from addons/ONNXRuntime/jetFlavourHelper.py import JetFlavourHelper



import importlib.util
import os

# Path to the Python file
file_path = os.path.join('addons', 'ONNXRuntime','python', 'jetFlavourHelper.py')

# Load the module dynamically
spec = importlib.util.spec_from_file_location("jetFlavourHelper", file_path)
jet_flavour_helper = importlib.util.module_from_spec(spec)
spec.loader.exec_module(jet_flavour_helper)


JetFlavourHelper = jet_flavour_helper.JetFlavourHelper




from addons.FastJet.jetClusteringHelper import ExclusiveJetClusteringHelper

#print(addons.ONNXRuntime.jetFlavourHelper.__file__)
print("!!! Jim: model_name used: ", model_name)

jetFlavourHelper = None
jetClusteringHelper = None

# Mandatory: RDFanalysis class where the use defines the operations on the TTree
class RDFanalysis:
    # __________________________________________________________
    # Mandatory: analysers funtion to define the analysers to process, please make sure you return the last dataframe, in this example it is df2
    def analysers(df):
        global jetClusteringHelper
        global jetFlavourHelper

        import sys
        #Jim
        sys.path.insert(0,'/fs/ddn/sdf/group/atlas/d/dntounis/Hss_setup_test/FCCAnalyses_Winter2023')
        import examples.FCCee.weaver.config
        print(examples.FCCee.weaver.config.__file__)

        from examples.FCCee.weaver.config import collections, njets

        tag = ""

        ## define jet clustering parameters
        jetClusteringHelper = ExclusiveJetClusteringHelper(collections["PFParticles"], njets, tag)

        ## run jet clustering
        df = jetClusteringHelper.define(df)

        ## define jet flavour tagging parameters

        jetFlavourHelper = JetFlavourHelper(
            collections,
            jetClusteringHelper.jets,
            jetClusteringHelper.constituents,
            tag,
        )

        ## define observables for tagger
        df = jetFlavourHelper.define(df)

        ## tagger inference
        df = jetFlavourHelper.inference(weaver_preproc, weaver_model, df)

        return df

    # __________________________________________________________
    # Mandatory: output function, please make sure you return the branchlist as a python list
    def output():

        ##  outputs jet properties
        branchList = jetClusteringHelper.outputBranches()

        ## outputs jet scores and constituent breakdown
        branchList += jetFlavourHelper.outputBranches()

        return branchList
