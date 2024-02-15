#!/usr/bin/env python3
# import warnings
# warnings.filterwarnings("error")
from plot_utils import *
from mappings import workflow_indices
from mappings import platform_configs

import sys

sys.path.append('../')
from extract_scripts.pretty_dict import pretty_dict

def plot_per_workflow_table(result_dicts, workflows, clusters):
    sophistication_levels = ["noise", "no_contention_yes_amdahl_noise",
                             "yes_contention_no_amdahl_noise", "no_contention_no_amdahl_noise"]


    sophistication_levels_printed_row2 = {
        "noise": r"\CA",
        "yes_contention_no_amdahl_noise": r"\Ca",
        "no_contention_no_amdahl_noise": r"\ca",
        "no_contention_yes_amdahl_noise": r"\cA",
    }



    noise_level = 0.0
    dfb_threshold = 10

    # pretty_dict(results_dict)
    data_points = {}
    for workflow in workflows:
        data_points[workflow] = {}
        for sophistication_level in sophistication_levels:
            data_points[workflow][sophistication_level] = []

    for workflow in data_points:
        for sophistication_level in sophistication_levels:
            for cluster in clusters:
                # print(f"{noise_level} {sophistication_level} {workflow} {cluster}")
                makespans = result_dicts[sophistication_level][noise_level][noise_level][workflow][cluster]["us"]
                best_makespan = float(min(result_dicts["basic_algorithms"][workflow][cluster].values()))
                for makespan in makespans:
                    dfb = dgfb(best_makespan, makespan)
                    data_points[workflow][sophistication_level].append(dfb)

    print(r"\begin{table}")
    print(r"\scriptsize")
    print(r"\caption{XXX}")
    print(r"\begin{center}")
    print(r"\begin{tabular}{l|c|c|c|c}")
    print(r"\toprule")
    sys.stdout.write(" ")
    sys.stdout.write(" Workflow ")
    for sophistication_level in sophistication_levels:
        sys.stdout.write("& " + sophistication_levels_printed_row2[sophistication_level])
    print(r"\\")
    print(r"\midrule")
    flip = 0
    for workflow in workflows:
        flip = 1 - flip
        if flip == 0:
            print(r"\rowcolor{Gray}")

        workflow_shortname = workflow.split("-")[0]
        if workflow_shortname == "1000genome":
            workflow_shortname = "genome"
        sys.stdout.write("$W_{\\" + workflow_shortname + "}$")
        for sophistication_level in sophistication_levels:
            value = 100 * sum([x <= dfb_threshold for x in data_points[workflow][sophistication_level]]) / len(data_points[workflow][sophistication_level])
            sys.stdout.write(" & " + "{:0.2f}".format(value))
        print(r"\\")
    print(r"\bottomrule")
    print(r"\end{tabular}")
    print(r"\end{center}")
    print(r"\end{table}")


def plot_simulator_sophistication_dfbs(plot_path, plot_name, result_dicts, workflows, clusters):

    sophistication_levels = ["noise", "no_contention_yes_amdahl_noise", "yes_contention_no_amdahl_noise",
                             "no_contention_no_amdahl_noise"]



    noise_levels = result_dicts[sophistication_levels[0]].keys()
    # pretty_dict(results_dict)
    data_points = {}
    for noise_level in noise_levels:
        data_points[noise_level] = {}
        for sophistication_level in sophistication_levels:
            data_points[noise_level][sophistication_level] = []

    for noise_level in data_points:
        for sophistication_level in sophistication_levels:
            for workflow in workflows:
                for cluster in clusters:
                    # print(f"{noise_level} {sophistication_level} {workflow} {cluster}")
                    makespans = result_dicts[sophistication_level][noise_level][noise_level][workflow][cluster]["us"]
                    best_makespan = float(min(result_dicts["basic_algorithms"][workflow][cluster].values()))
                    for makespan in makespans:
                        dfb = dgfb(best_makespan, makespan)
                        data_points[noise_level][sophistication_level].append(dfb)

    fontsize = 12

    for noise_level in noise_levels:
        output_filename = plot_path + "sophistication_noise_" + str(noise_level) + "_" + plot_name + ".pdf"
        f, ax1 = plt.subplots(1, 1, sharey=True, figsize=(6, 6))
        ax1.yaxis.grid()

        colors = {
            "no_contention_no_amdahl_noise": "r",
            "no_contention_yes_amdahl_noise": "g",
            "yes_contention_no_amdahl_noise": "b",
            "noise": "k"}

        zorders = {
            "noise": 3,
            "yes_contention_no_amdahl_noise": 2,
            "no_contention_no_amdahl_noise": 1,
            "no_contention_yes_amdahl_noise": 0,
        }

        labels = {
            "no_contention_no_amdahl_noise": r"$\bar{C}\bar{A}$",
            "no_contention_yes_amdahl_noise": r"$\bar{C}A$",
            "yes_contention_no_amdahl_noise": r"$C\bar{A}$",
            "noise": "$CA$"}

        for sophistication_level in sophistication_levels:
            cdf_values = []
            dfb_values = [x/10.0 for x in range(0, 1000, 1)]
            for dfb_value in dfb_values:
                cdf_values.append(100 * sum([x <= dfb_value for x in data_points[noise_level][sophistication_level]]) /
                                  len(data_points[noise_level][sophistication_level]))

            ax1.plot(dfb_values, cdf_values, colors[sophistication_level] + "-",
                     linewidth=2, label=labels[sophistication_level], zorder=zorders[sophistication_level])

        plt.xticks(range(0,101,10), fontsize=fontsize+2)
        plt.yticks(fontsize=fontsize+2)
        plt.grid(which='both', linestyle=':')
        plt.xlabel("% degradation from best (dfb)", fontsize=fontsize+2)
        plt.ylabel("Fraction of experimental scenarios (%)", fontsize=fontsize+2)
        plt.ylim([20, 102])

        plt.legend(fontsize=fontsize+2)
        plt.savefig(output_filename)
        plt.close()
        sys.stderr.write("Generated plot '" + output_filename + "'\n")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.stderr.write("Usage: " + sys.argv[0] + " <version>\n")
        sys.exit(1)

    plot_path, result_dicts, workflows, clusters, best_algorithm_on_average = \
        importData(sys.argv[1], file_factor=1, verbosity=1)

    # platforms = clusters
    platforms = clusters[0:3]

    plot_per_workflow_table(result_dicts, workflows, platforms)

    plot_simulator_sophistication_dfbs(plot_path, "ALL", result_dicts, workflows, platforms)

    for workflow in workflows:
        plot_simulator_sophistication_dfbs(plot_path, workflow.split("-")[0], result_dicts, [workflow], platforms)

