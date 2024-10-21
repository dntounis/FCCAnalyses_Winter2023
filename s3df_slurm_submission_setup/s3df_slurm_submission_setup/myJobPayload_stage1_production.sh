#!/bin/bash
# This is the payload script that runs the actual job commands

flavor=$1
number=$2
detector=$3

echo "Running weaver stage 1 for flavor $flavor - number $number - detector $detector"

#cd Hss_setup_test/whizard_v2/
cd /fs/ddn/sdf/group/atlas/d/dntounis/Hss_setup_test/FCCAnalyses_Winter2023

source setup.sh

#fccanalysis run examples/FCCee/weaver/stage1.py --output outputs_stage1/test_H${flavor}_DELPHES_IDEA_Winter2023_v2_${number}.root --files-list ${HOME}/Hss_setup_test/Delphes/zhiggs_${flavor}/zhiggs_nunu_${flavor}_DELPHES_IDEA_Winter2023_${number}.edm4hep.root

fccanalysis run examples/FCCee/weaver/stage1.py --output outputs_stage1_production_for_training_Oct2024/${detector}/test_H${flavor}_DELPHES_${detector}_Winter2023_${number}.root --files-list ${HOME}/Hss_setup_test/Delphes/production_for_training_Oct2024/zhiggs_${flavor}_${detector}_Oct24/zhiggs_nunu_${flavor}_DELPHES_${detector}_Winter2023_${number}.edm4hep.root
