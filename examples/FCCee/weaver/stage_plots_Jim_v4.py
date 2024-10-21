'''
Jim: 5 Oct 2024 stage2 plots but overlaying distributios for different detector types

'''
import ROOT
ROOT.gROOT.SetBatch(True) #Jim
import os
import argparse

# Dictionary to assign unique colors to each flavor
#flavor_colors = {
#    "u": ROOT.kRed,
#    "d": ROOT.kBlue,
#    "c": ROOT.kGreen,
#    "s": ROOT.kOrange,
#    "b": ROOT.kViolet,
#    #"tau": ROOT.kMagenta,
#    "g": ROOT.kCyan
#}

flavor_colors = {
    "q": ROOT.kOrange,
    "c": ROOT.kGreen,
    "s": ROOT.kBlue,
    "b": ROOT.kRed,
    "g": ROOT.kPink+9
}

# ________________________________________________________________________________
def main():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--indir",
        help="path input directory",
        default="/tmp/selvaggi/data/pre_winter2023_tests_v2/selvaggi_2022Nov24",
    )
    parser.add_argument(
        "--outdir",
        help="path output directory",
        default="/eos/user/s/selvaggi/www/test_tag",
    )

    args = parser.parse_args()

    # Enable multi-threading
    ROOT.ROOT.EnableImplicitMT()

    #Jim
    import sys
    #sys.path.insert(0,'/sdf/home/d/dntounis/Hss/FCCAnalyses_Winter2023')
    sys.path.insert(0,'/fs/ddn/sdf/group/atlas/d/dntounis/Hss_setup_test/FCCAnalyses_Winter2023')
    #local_config_path = '/fs/ddn/sdf/group/atlas/d/dntounis/Hss_setup_test/FCCAnalyses_Winter2023/examples/FCCee/weaver/config'
    #sys.path.insert(0,'~/Hss_setup_test/FCCAnalyses_Winter2023')

    import examples.FCCee.weaver.config_3flavors_Jim_plotting_only
    print(examples.FCCee.weaver.config_3flavors_Jim_plotting_only.__file__)

    from examples.FCCee.weaver.config_3flavors_Jim_plotting_only import variables_pfcand, variables_jet,variables_event, flavors

    input_dir = args.indir
    output_dir = args.outdir

    os.system("mkdir -p {}".format(output_dir))




    # Loop over the flavors and assign samples
    samples = []
    # these should be the flavors:  = ["c","s","b"]
    for f in flavors:
        sample_IDEA = {
            "file": "{}/SiD_o2_v04_C/test_H{}{}_DELPHES_SiD_o2_v04_C_Winter2023_MERGED.root".format(input_dir, f, f),
        "flavor": f,
            "label": "IDEA",
        }

        sample_SiD_o2_v04_C = {
            "file": "{}/IDEA/test_H{}{}_DELPHES_IDEA_Winter2023_MERGED.root".format(input_dir, f, f),
            "flavor": f,
            "label": "SiD_C",
        }

        sample_SiD_o2_v04_D = {
            "file": "{}/SiD_o2_v04_D/test_H{}{}_DELPHES_SiD_o2_v04_D_Winter2023_MERGED.root".format(input_dir, f, f),
            "flavor": f,
            "label": "SiD_D",
        }


        samples.append(sample_SiD_o2_v04_C)
        samples.append(sample_IDEA)
        samples.append(sample_SiD_o2_v04_D)

    # Loop over the samples and assign histograms
    for sample in samples:
        df = ROOT.RDataFrame("tree", sample["file"])
        #df = ROOT.RDataFrame("events", sample["file"])
        sample["histos_pfcand"] = dfhs_pfcand(df, variables_pfcand)
        sample["histos_jet"] = dfhs_jet(df, variables_jet)
        #sample["histos_event"] = dfhs_event(df, variables_event)

        # RunGraphs allows to run the event loops of the separate RDataFrame graphs
        # concurrently. This results in an improved usage of the available resources
        # if each separate RDataFrame can not utilize all available resources, e.g.,
        ROOT.RDF.RunGraphs(
            list(sample["histos_pfcand"].values())
            + list(sample["histos_jet"].values())
            #+ list(sample["histos_event"].values())
        )

    # Loop over the samples and plot the histograms
    for var, params in variables_pfcand.items():
        plot(samples, "histos_pfcand", var, params, output_dir)
    for var, params in variables_jet.items():
        plot(samples, "histos_jet", var, params, output_dir)
    #for var, params in variables_event.items():
    #    plot(samples, "histos_event", var, params, output_dir) 


# _______________________________________________________________________________
def dfhs_pfcand(df, vars):

    ## extract charged particles
    #df_charged = df.Filter("All(abs(pfcand_charge)>0)", "select charged constituents")
    df_charged = df

    ## order constituents in energy
    df_sorted_e = df_charged.Define("e_sorted_id", "Reverse(Argsort(pfcand_e))")

    df_dict = dict()

    for pfcand_var, params in vars.items():
        df_var = df_sorted_e.Redefine(pfcand_var, "Take({}, e_sorted_id)".format(pfcand_var))
        var = pfcand_var.replace("pfcand_", "")
        df_var = df_var.Define(var, "{}[0]".format(pfcand_var))
        df_dict[pfcand_var] = df_var.Histo1D(
            (
                "h_{}".format(var),
                ";{};N_{{Events}}".format(params["title"]),
                params["bin"],
                params["xmin"],
                params["xmax"],
            ),
            var,
        )
    return df_dict


# _______________________________________________________________________________
def dfhs_jet(df, vars):

    ## extract charged particles
    # df_charged = df.Filter("All(abs(pfcand_charge)>0)", "select charged constituents")
    

    df_dict = dict()
    for jet_var, params in vars.items():
        df_dict[jet_var] = df.Histo1D(
            (
                "h_{}".format(jet_var),
                ";{};N_{{Events}}".format(params["title"]),
                params["bin"],
                params["xmin"],
                params["xmax"],
            ),
            jet_var,
        )
    return df_dict


# _______________________________________________________________________________
def dfhs_event(df, vars):

    ## extract charged particles
    # df_charged = df.Filter("All(abs(pfcand_charge)>0)", "select charged constituents")
    
    df_dict = dict()
    for event_var, params in vars.items():
        print(event_var)
        df_dict[event_var] = df.Histo1D(
            (
                "h_{}".format(event_var),
                ";{};N_{{Events}}".format(params["title"]),
                params["bin"],
                params["xmin"],
                params["xmax"],
            ),
            event_var,
        )
    return df_dict


# _______________________________________________________________________________
def plot(samples, histo_coll, var, params, outdir):

    dfhs = []
    for sample in samples:
        dfhs.append(sample[histo_coll][var].GetValue())


    # Create canvas with pads for main plot and data/MC ratio
    c = ROOT.TCanvas("c", "", 700, 750)

    ROOT.gStyle.SetOptStat(0)
    upper_pad = ROOT.TPad("upper_pad", "", 0, 0.35, 1, 1)
    lower_pad = ROOT.TPad("lower_pad", "", 0, 0, 1, 0.35)
    for p in [upper_pad, lower_pad]:
        p.SetLeftMargin(0.14)
        p.SetRightMargin(0.05)
        p.SetTickx(False)
        p.SetTicky(False)
    upper_pad.SetBottomMargin(0)
    lower_pad.SetTopMargin(0)
    lower_pad.SetBottomMargin(0.3)
    upper_pad.Draw()
    lower_pad.Draw()

    # Draw the histograms
    upper_pad.cd()
    if params["scale"] == "log":
        upper_pad.SetLogy()
        
    # Define line styles for each detector type
    line_styles = {
        "IDEA": 2,    # Dashed line
        "SiD_C": 1,   # Solid line
        "SiD_D": 9    # dash-Dotted line
    }

    line_widths = {
        "IDEA": 2,    # Dashed line
        "SiD_C": 2,   # Solid line
        "SiD_D": 3    # dash-Dotted line
    }

    for i, dfh in enumerate(dfhs):
        #dfh.SetLineWidth(2)
        dfh.SetLineColor(flavor_colors[samples[i]["flavor"]])
        
        # Set line style based on the detector label
        dfh.SetLineStyle(line_styles[samples[i]["label"]])
        dfh.SetLineWidth(line_widths[samples[i]["label"]])

        dfh.GetYaxis().SetLabelSize(0.045)
        dfh.GetYaxis().SetTitleSize(0.05)
        dfh.SetStats(0)
        dfh.SetTitle("")
        
        if i == 0:
            dfh.Draw("hist")
        else:
            dfh.Draw("hist SAME")






    # Draw the ratio
    lower_pad.cd()
    ratio = ROOT.TH1I(
        "zero",
        "",
        params["bin"],
        params["xmin"],
        params["xmax"],
    )
    ratio.SetLineColor(ROOT.kBlack)
    #ratio.SetLineStyle(2)
    ratio.SetLineStyle(line_styles[samples[i]["label"]])
    ratio.SetLineWidth(2)
    ratio.SetMinimum(0.0)
    ratio.SetMaximum(2.0)
    ratio.GetXaxis().SetLabelSize(0.08)
    ratio.GetXaxis().SetTitleSize(0.12)
    ratio.GetXaxis().SetTitleOffset(1.0)
    ratio.GetYaxis().SetLabelSize(0.08)
    ratio.GetYaxis().SetTitleSize(0.09)
    ratio.GetYaxis().SetTitle("ratio")
    ratio.GetYaxis().CenterTitle()
    ratio.GetYaxis().SetTitleOffset(0.7)
    # ratio.GetYaxis().SetNdivisions(503, False)
    ratio.GetYaxis().ChangeLabel(-1, -1, 0)
    ratio.GetXaxis().SetTitle(params["title"])
    ratio.Draw("AXIS")

    #ratiodata ordering c-c-c-s-s-s-b-b-b
    ratiodata_list = []
    base_hist_c = dfhs[0].Clone()
    base_hist_s = dfhs[3].Clone()
    base_hist_b = dfhs[6].Clone()

    base_hist_c.Sumw2()
    base_hist_s.Sumw2()
    base_hist_b.Sumw2()

    for i, dfh in enumerate(dfhs):
        ratiodata = dfh.Clone()
        ratiodata.Sumw2()
        if samples[i]["flavor"] == "c":
            ratiodata.Divide(base_hist_c)
        elif samples[i]["flavor"] == "s":
            ratiodata.Divide(base_hist_s)
        elif samples[i]["flavor"] == "b":
            ratiodata.Divide(base_hist_b)
        ratiodata.SetLineColor(flavor_colors[samples[i]["flavor"]])
        ratiodata.SetMarkerColor(flavor_colors[samples[i]["flavor"]])
        ratiodata_list.append(ratiodata)

    for ratiodata in ratiodata_list:
        ratiodata.Draw("same e")


    # Add legend
    upper_pad.cd()
    legend = ROOT.TLegend(0.65, 0.45, 0.94, 0.85)
    legend.SetTextFont(42)
    legend.SetFillStyle(0)
    legend.SetBorderSize(0)
    legend.SetTextSize(0.045)
    legend.SetTextAlign(12)
    for i, sample in enumerate(samples):
        legend.AddEntry(dfhs[i], "{} ({}-jets)".format(sample["label"], sample["flavor"]), "l")
    legend.Draw()

    # Add ATLAS label
    text = ROOT.TLatex()
    text.SetNDC()
    text.SetTextFont(72)
    text.SetTextSize(0.05)
    text.SetTextFont(42)
    text.DrawLatex(0.20, 0.91, "(Delphes)")
    text.SetTextSize(0.04)
    text.DrawLatex(0.35, 0.91, "e^{+}e^{-} #rightarrow Z (#nu #nu) H (j j)")
    text.SetTextSize(0.04)
    #text.DrawLatex(0.22, 0.68, "j = u,d,c,s,b,g")
    #text.SetTextSize(0.05)
    text.SetTextAlign(31)
    text.DrawLatex(0.95, 0.91, "#sqrt{s} = 250 GeV")
    
    # Save the plot
    figpath = "{}/{}.pdf".format(outdir, var)
    c.SaveAs(figpath)



# _______________________________________________________________________________________
if __name__ == "__main__":
    main()


