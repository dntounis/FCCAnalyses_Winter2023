#!/bin/bash
# This is the payload script that runs the actual job commands

flavor=$1
number=$2

echo "Running weaver stage 1 for flavor $flavor - number $number"

#cd Hss_setup_test/whizard_v2/
cd /fs/ddn/sdf/group/atlas/d/dntounis/Hss_setup_test/FCCAnalyses_Winter2023

source setup.sh

#fccanalysis run examples/FCCee/weaver/stage1.py --output outputs_stage1/test_H${flavor}_DELPHES_IDEA_Winter2023_v2_${number}.root --files-list ${HOME}/Hss_setup_test/Delphes/zhiggs_${flavor}/zhiggs_nunu_${flavor}_DELPHES_IDEA_Winter2023_${number}.edm4hep.root

fccanalysis run examples/FCCee/weaver/stage1.py --output outputs_stage1/test_H${flavor}_DELPHES_SiD_o2_v04_Winter2023_v2_${number}_C.root --files-list ${HOME}/Hss_setup_test/Delphes/zhiggs_${flavor}/zhiggs_nunu_${flavor}_DELPHES_SiD_o2_v04_C_Winter2023_${number}.edm4hep.root
