#!/bin/bash
# This is the payload script that runs the actual job commands

flavor=$1
detector=$2
number=$3

echo "Running inference for flavor $flavor - detector $detector"

#cd Hss_setup_test/whizard_v2/
cd /fs/ddn/sdf/group/atlas/d/dntounis/Hss_setup_test/FCCAnalyses_Winter2023

source setup.sh

fccanalysis run examples/FCCee/weaver/analysis_inference.py --output outputs_inference_production_for_training_Oct2024/${detector}/infer_H${flavor}_DELPHES_${detector}_Winter2023_${number}.root --files-list ../Delphes/production_for_training_Oct2024/zhiggs_${flavor}_${detector}_Oct24/zhiggs_nunu_${flavor}_DELPHES_${detector}_Winter2023_${number}.edm4hep.root --ncpus 4
