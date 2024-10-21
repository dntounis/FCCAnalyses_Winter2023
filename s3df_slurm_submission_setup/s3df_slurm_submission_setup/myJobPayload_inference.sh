#!/bin/bash
# This is the payload script that runs the actual job commands

flavor=$1

echo "Running inference for flavor $flavor"

#cd Hss_setup_test/whizard_v2/
cd /fs/ddn/sdf/group/atlas/d/dntounis/Hss_setup_test/FCCAnalyses_Winter2023

source setup.sh

fccanalysis run examples/FCCee/weaver/analysis_inference.py --output outputs_inference_PNet_Hss_SiD_o2_vo4_Winter2023_C_27epochs/infer_H${flavor}_DELPHES_SiD_o2_v04_Winter2023_C.root --files-list ${HOME}/Hss_setup_test/Delphes/zhiggs_${flavor}/zhiggs_nunu_${flavor}_DELPHES_SiD_o2_v04_C_Winter2023_{7..9}.edm4hep.root  --ncpus 64