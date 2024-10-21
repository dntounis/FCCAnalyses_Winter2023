#!/bin/bash
# This is the payload script that runs the actual job commands

flavor=$1
number=$2

echo "Running weaver stage 2 for flavor $flavor - number $number"

#cd Hss_setup_test/whizard_v2/
cd /fs/ddn/sdf/group/atlas/d/dntounis/Hss_setup_test/FCCAnalyses_Winter2023

source setup.sh

#python examples/FCCee/weaver/stage2.py outputs_stage1/test_H${flavor}_DELPHES_IDEA_Winter2023_v2_${number}.root outputs_stage2/out_H${flavor}_DELPHES_IDEA_Winter2023_v2_${number}.root 0 50000

python examples/FCCee/weaver/stage2.py outputs_stage1/test_H${flavor}_DELPHES_SiD_o2_v04_Winter2023_v2_${number}_C.root outputs_stage2/out_H${flavor}_DELPHES_SiD_o2_v04_Winter2023_v2_${number}_C.root 0 50000

