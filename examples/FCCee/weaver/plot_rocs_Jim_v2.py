#Jim
import sys
sys.path.insert(0,'/home/dntounis/Hss_setup_test/FCCAnalyses_Winter2023/')

import examples.FCCee.weaver.config
print(examples.FCCee.weaver.config.__file__)

from matplotlib.lines import Line2D


import ROOT
import os
import argparse
import numpy as np
import glob
#import sys
from collections import OrderedDict
from copy import deepcopy

#Jim
#sys.path.insert(0,'/sdf/home/d/dntounis/Hss/FCCAnalyses_Winter2023')

#import examples.FCCee.weaver.config
#print(examples.FCCee.weaver.config.__file__)


from examples.FCCee.weaver.config import variables_pfcand, variables_jet, flavors
#Jim
print("flavors=",flavors)
import matplotlib.pyplot as plt

#plt.rcParams["mathtext.fontset"] = "stix"
#plt.rcParams["font.family"] = "STIXGeneral"
plt.rcParams["axes.labelweight"] = "bold"
#plt.rcParams['text.usetex'] = True
plt.rcParams['font.family'] = 'sans-serif' #serif

plt.gcf().subplots_adjust(bottom=0.15)


# compute binary discriminant
ROOT.gInterpreter.Declare(
    """
ROOT::VecOps::RVec<float> binary_discriminant(ROOT::VecOps::RVec<float> score_s, ROOT::VecOps::RVec<float> score_b)
{
    ROOT::VecOps::RVec<float> out;
    for (int i=0; i<score_s.size(); i++) {
        float den = score_s.at(i) + score_b.at(i);
        float d = (den > 0) ? score_s.at(i) / den : 0;
        //std::cout<<i<<", "<<d<<std::endl;
        out.push_back(d);
    }
    return out;
}
"""
)

# Enable multi-threading
ROOT.ROOT.EnableImplicitMT()

# ________________________________________________________________________________
def main():
    
    parser = argparse.ArgumentParser()
    parser.add_argument("--detector", type=str, default="SiD_o2_v04_C", help="detector to run inference for")
    args = parser.parse_args()

    output_directory = f"outputs_inference_production_for_training_Oct2024/{args.detector}"

    proc_sid_test_Jim = Process(
        "wzp6_pnet",
        "test",
        "WZ-Pythia (PNet)",
        #"outputs_inference_Hssv1",
        output_directory,
    )


    samples = dict()

    nfiles_max = 30
    ### retrieve samples

    # processes = [proc_pnet, proc_pt]
    #processes = [proc_pt, proc_pt2]
    processes = [proc_sid_test_Jim]

    for proc in processes:
        samples[proc] = dict()
        for f in flavors:
            fs = f

            files = []
            #dirpath = "{}/{}_H{}{}_ecm250/".format(proc.dir, proc.name, fs, fs)
            dirpath = "{}/infer_H{}{}/".format(proc.dir,fs, fs)
            print("--- Jim: dirpath =",dirpath)
            #dirpath = "{}/".format(proc.dir)
            for i, fname in enumerate(glob.glob("{}/*.root".format(dirpath))):
                if i >= nfiles_max:
                    continue
                files.append(fname)

            # print(files)
            samples[proc][f] = Sample(files, "events", f, proc)
            #samples[proc][f] = Sample(files, "Events", f, proc)

    roc_param = RocParam(2, 100)  # ndecades, nbins
    title = f"{args.detector} (Delphes)"
    plot_param = PlotParams(
        [Text(title, (0.75, 1.03), "bold", 13)],
        ((0.0, 1.0), (0.001, 1.0)), #Jim: change 0.3 to 0.0 x axis lower range
        ("jet tagging efficiency", "jet misid. probability"),
        ("linear", "log"),
    )

    ctag_cfg = {
        "sig": "c",
        #"bkg": ["g", "u","d","s", "b"],
        "bkg": ["g", "q","b", "s"],
        "samples": samples,
        "variants": processes,
        "param_roc": roc_param,
        "param_plot": plot_param,
    }

    btag_cfg = deepcopy(ctag_cfg)
    btag_cfg["sig"] = "b"
    #btag_cfg["bkg"] = ["g", "u","d","s", "c"]
    btag_cfg["bkg"] = ["g", "q","c", "s"] #order to match IDEA plots!!!
    btag_cfg["param_plot"].ranges = ((0.0, 1.0), (0.001, 1.0))


    stag_cfg = deepcopy(ctag_cfg)
    stag_cfg["sig"] = "s"
    #stag_cfg["bkg"] = ["g", "u","d", "c", "b"]
    stag_cfg["bkg"] = ["q", "g", "c", "b"]
    stag_cfg["param_plot"].ranges = ((0.0, 1.0), (0.001, 1.0))

    gtag_cfg = deepcopy(ctag_cfg)
    gtag_cfg["sig"] = "g"
    #gtag_cfg["bkg"] = ["u","d", "s", "c", "b"]
    gtag_cfg["bkg"] = ["q", "s", "c", "b"]
    gtag_cfg["param_plot"].ranges = ((0.0, 1.0), (0.001, 1.0))

    roc_plot(ctag_cfg,args)
    roc_plot(btag_cfg,args)
    roc_plot(stag_cfg,args)
    roc_plot(gtag_cfg,args)


# _______________________________________________________________________________
class Sample:
    def __init__(self, files, treename, flavor, label):
        self.files = files
        self.treename = treename
        self.flavor = flavor
        self.label = label


# _______________________________________________________________________________
class Process:
    def __init__(self, procname, name, label, dir):
        self.procname = procname
        self.name = name
        self.label = label
        self.dir = dir


# _______________________________________________________________________________
class RocParam:
    def __init__(self, ndec, nbins):
        self.ndec = ndec  # how many decades for log scale
        self.nbins = nbins


# _______________________________________________________________________________
class ROC:
    def __init__(self, name, sample_s, sample_b, param, color, style):
        self.name = name
        self.sample_s = sample_s
        self.sample_b = sample_b
        self.range = param.ndec
        self.nbins = param.nbins
        self.color = color
        self.style = style
        self.x = []
        self.y = []

        # self.name = "{}_{}".format(self.sample_s.flavor, self.sample_b.flavor)
        self.label = "{} vs {} ({})".format(self.sample_s.flavor, self.sample_b.flavor, self.sample_s.label.label)
        ## initialize histo rdataframe objects
        self.histos = []
        df_s = ROOT.RDataFrame(self.sample_s.treename, self.sample_s.files)
        df_b = ROOT.RDataFrame(self.sample_b.treename, self.sample_b.files)

        ## dict of rdf histos vs cut values
        self.dh_s = dfhs(
            df_s,
            self.sample_s.flavor,
            self.sample_b.flavor,
            self.range,
            self.nbins,
            "sig_{}".format(self.name),
        )
        self.dh_b = dfhs(
            df_b,
            self.sample_s.flavor,
            self.sample_b.flavor,
            self.range,
            self.nbins,
            "bkg_{}".format(self.name),
        )

        self.dhs = list(self.dh_s.values()) + list(self.dh_b.values())

    def get_roc(self):
        out_root = ROOT.TFile("{}.root".format(self.name), "RECREATE")
        for cut, hist in self.dh_s.items():
            hist.Write()
        for cut, hist in self.dh_b.items():
            hist.Write()

        x, y = [], []
        cuts = list(self.dh_s.keys())

        def integral(h):
            return float(h.Integral(0, h.GetNbinsX() + 1))

        sum_s = integral(self.dh_s[cuts[0]])
        sum_b = integral(self.dh_b[cuts[0]])

        if sum_s == 0 or sum_b == 0:
            sys.exit("ERROR: histograms are empty...")

        for cut in cuts:
            x.append(integral(self.dh_s[cut]) / sum_s)
            y.append(integral(self.dh_b[cut]) / sum_b)

        self.x = x
        self.y = y

        return x, y


# _______________________________________________________________________________
class Text:
    def __init__(self, text, location, weight, size):
        self.text = text
        self.location = location
        self.weight = weight
        self.size = size


# _______________________________________________________________________________
class PlotParams:
    def __init__(self, texts, ranges, axlabels, scales):
        self.texts = texts
        self.ranges = ranges
        self.axlabels = axlabels
        self.scales = scales


# _______________________________________________________________________________
class Graph:
    def __init__(self, rocs, params, fig_file):
        self.rocs = rocs
        self.texts = params.texts
        self.ranges = params.ranges
        self.titles = params.axlabels
        self.scales = params.scales
        self.fig_file = fig_file

        fig, ax = plt.subplots()

        ## plot curves

        print(fig_file)
        for roc in rocs:
            print(
                roc.name,
                roc.sample_s.label.label,
                roc.sample_b.label.label,
            )
            for x, y in zip(roc.x, roc.y):
                print(x, y)

            ax.plot(
                roc.x,
                roc.y,
                linestyle=roc.style,
                color=roc.color,
                label="{}".format(roc.label),
                linewidth=3,
            )

        # add text to plot
        for text in self.texts:
            ax.text(
                text.location[0],
                text.location[1],
                text.text,
                verticalalignment="center",
                horizontalalignment="center",
                transform=ax.transAxes,
                weight=text.weight,
                fontsize=text.size,
            )

        handles, labels = ax.get_legend_handles_labels()
        ax.legend(
            labels=labels,
            frameon=False,
            # loc=self.leg_loc,
            loc='best',
            fontsize=12,
        )

        # Define the legend handles (lines) manually
        legend_elements = [
            Line2D([0], [0], color='black', lw=3, label='b vs g'),
            Line2D([0], [0], color='red', lw=3, label='b vs q'),
            Line2D([0], [0], color='blue', lw=3, label='b vs c'),
            Line2D([0], [0], color='magenta', lw=3, label='b vs s')
        ]

        # Add the legend to your plot
        ax.legend(handles=legend_elements, loc='best', fontsize=12, frameon=False)



        ax.grid(linestyle="dashed")
        ax.tick_params(which='both', direction='in', top=True, right=True, labelsize=14) #Jim

        ax.set_xlabel(self.titles[0], fontsize=14)
        ax.set_ylabel(self.titles[1], fontsize=14)
        ax.set_xscale(self.scales[0])
        ax.set_yscale(self.scales[1])

        ax.set_xlim(self.ranges[0][0], self.ranges[0][1])
        ax.set_ylim(self.ranges[1][0], self.ranges[1][1])

        fig.tight_layout()
        fig.savefig(fig_file)


# _______________________________________________________________________________
def roc_plot(cfg,args):

    colors = ["black", "red", "blue", "magenta", "green"]
    styles = ["-", "--", "-.", "."]

    rocs = []

    procstr = ""
    for ip, proc in enumerate(cfg["variants"]):
        sig_f = cfg["sig"]
        procstr += "_{}".format(proc.name)
        for ib, bkg_f in enumerate(cfg["bkg"]):
            name = "{}{}_{}".format(sig_f, bkg_f, proc.name)
            rocs.append(
                ROC(
                    name,
                    cfg["samples"][proc][sig_f],
                    cfg["samples"][proc][bkg_f],
                    cfg["param_roc"],
                    colors[ib],
                    styles[ip],
                )
            )

    dh_list = []
    for roc in rocs:
        dh_list += roc.dhs

    ROOT.RDF.RunGraphs(dh_list)

    for roc in rocs:
        roc.get_roc()

    plot_name = "{}tagging{}".format(cfg["sig"], procstr)
    plot = Graph(rocs, cfg["param_plot"], "plots_roc_{}/{}.pdf".format(args.detector,plot_name))


# ______________________________________________________________________________
def dfhs(df, fs, fb, m, nbins, label):

    lin_array = np.arange(0.0, m + float(m) / nbins, float(m) / nbins)
    exp_array = np.power(10.0, lin_array)

    a = -1.0 / (np.power(10.0, m) - 1)
    b = np.power(10.0, m) / (np.power(10.0, m) - 1)
    cutvals = a * exp_array + b
    cutvals.sort()

    score_s = "recojet_is{}".format(fs.upper())
    #score_b = "recojet_is{}".format(fb.upper())

    #Jim
    #if fb == "u" or fb =="d":
    #    fb="q"
    
    score_b = "recojet_is{}".format(fb.upper())


    binary_discr_var = "d_{}{}".format(fs, fb)
    binary_discr_label = "D({},{})".format(fs, fb)
    binary_discr_func = "binary_discriminant({}, {})".format(score_s, score_b)

    # print(cutvals)
    df_dict = OrderedDict()
    dh_dict = OrderedDict()

    print("producing roc curve: {} vs {} -- {}".format(fs, fb, label))
    df = df.Define(binary_discr_var, binary_discr_func)

    for i, cut in enumerate(cutvals):

        cut_str = "{:.0f}".format(1e5 * cut)
        if i == 0:
            cut_str = "00000"

        filter_expr = "{} > {}".format(binary_discr_var, cut)
        fcoll_title = "{} > {:.4f}".format(binary_discr_label, cut)
        fcoll_str = "{}_{}".format(binary_discr_var, cut_str)

        # define filter from previous iteration in the loop
        if i == 0:
            df_dict[cut] = df.Define(fcoll_str, "{}[{}]".format(binary_discr_var, filter_expr))
        else:
            df_dict[cut] = df_dict[cutvals[i - 1]].Define(fcoll_str, "{}[{}]".format(binary_discr_var, filter_expr))

        dh_dict[cut] = df_dict[cut].Histo1D(
            (
                "h_{}_{}".format(fcoll_str, label),
                ";{};N_{{Events}}".format(binary_discr_label),
                nbins,
                0.0,
                1.0,
            ),
            fcoll_str,
        )
    return dh_dict


# _______________________________________________________________________________________
if __name__ == "__main__":
    main()
