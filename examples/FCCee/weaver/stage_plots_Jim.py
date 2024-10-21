import ROOT
ROOT.gROOT.SetBatch(True)  # For batch processing (no graphical output)

import os
import argparse

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

    import sys
    sys.path.insert(0, '/fs/ddn/sdf/group/atlas/d/dntounis/Hss_setup_test/FCCAnalyses_Winter2023')

    from examples.FCCee.weaver.config import variables_pfcand, variables_jet, variables_event, flavors

    input_dir = args.indir
    output_dir = args.outdir

    os.system("mkdir -p {}".format(output_dir))

    # Create a canvas for plotting
    c = ROOT.TCanvas("c", "c", 800, 800)
    
    # Dictionary to assign unique colors to each flavor
    flavor_colors = {
        "u": ROOT.kRed,
        "d": ROOT.kBlue,
        "c": ROOT.kGreen,
        "s": ROOT.kOrange,
        "b": ROOT.kViolet,
        "tau": ROOT.kMagenta,
        "g": ROOT.kCyan
    }

    # Use the flavors you requested
    flavors = ['u', 'd', 'c', 's', 'b', 'tau', 'g']
    for var, params in variables_jet.items():
        # Initialize the canvas
        c.Clear()
        if params["scale"] == "log":
            c.SetLogy()
        # Create a histogram stack to superimpose histograms
        hist_stack = ROOT.THStack()

        # Legend for the different flavors
        legend = ROOT.TLegend(0.55, 0.68, 0.926, 0.85)
        legend.SetTextFont(42)
        legend.SetFillStyle(0)
        legend.SetBorderSize(0)
        legend.SetTextSize(0.045)
        legend.SetTextAlign(12)

        for f in flavors:
            # Read files for this flavor
            file_path = "{}/out_H{}{}_DELPHES_SiD_o2_v04_Winter2023_v2_200K.root".format(input_dir, f, f)
            df = ROOT.RDataFrame("tree", file_path)

            # Create the histogram for this flavor and variable
            hist = df.Histo1D(("{}_{}".format(f, var), params["title"], params["nbins"], params["min"], params["max"]), var)

            hist.SetLineColor(flavor_colors[f])
            hist.SetLineWidth(2)

            # Add the histogram to the stack
            hist_stack.Add(hist.GetValue())

            # Add to the legend
            legend.AddEntry(hist.GetValue(), "{}-jets".format(f), "l")
        
        # Draw the histogram stack
        hist_stack.Draw("nostack hist")
        hist_stack.GetXaxis().SetTitle(params["title"])
        hist_stack.GetYaxis().SetTitle("Events")

        # Draw the legend
        legend.Draw()

        # Add text for description (modify as needed)
        text = ROOT.TLatex()
        text.SetNDC()
        text.SetTextFont(72)
        text.SetTextSize(0.05)
        text.DrawLatex(0.14, 0.91, "SiD")
        text.SetTextFont(42)
        text.DrawLatex(0.20, 0.91, "(Delphes)")
        text.SetTextSize(0.05)
        text.DrawLatex(0.25, 0.78, "e^{+}e^{-} #rightarrow Z (#nu #nu) H (j j)")
        text.SetTextSize(0.04)
        text.DrawLatex(0.28, 0.71, "j = u, d, c, s, b, tau, g")
        text.SetTextSize(0.05)
        text.SetTextAlign(31)
        text.DrawLatex(0.95, 0.91, "#sqrt{s} = 250 GeV, 10^{4} events")

        # Save the canvas to a file
        figpath = "{}/superimposed_{}.pdf".format(output_dir, var)
        c.SaveAs(figpath)

if __name__ == "__main__":
    main()
