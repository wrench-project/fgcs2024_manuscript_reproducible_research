#!/usr/bin/env python3
from plot_utils import *
from bisect import bisect

#
# Generate the basic algorithm "diversity" plot
###############################################
def generate_basic_algorithms_plot(plot_path, result_dict, best_on_average):
	x = compute_all_percent_diffs(result_dict);
	fontsize = 18
	output_file = plot_path + "baseline_algorithm_dfbs.pdf"

	values = range(len(x.keys()))
	y = [i[0] for i in x.values()]
	y = [max(d, 0.1) for d in y]

	f, ax = plt.subplots(1, 1, sharey=True, figsize=(14, 7))

	plt.grid(axis='y')
	plt.yscale("log")

	# plotting dots to represent algorithm
	i = 0
	ylim_max = 0
	dots = [dfb[1] for dfb in x.values()]
	for cluster in dots:
		for algo, diff in cluster.items():
			if algo != best_on_average:
				plt.plot(i, max(0.1, diff), 'x', markersize=5, color='0.4')
			else:
				plt.plot(i, max(0.1, diff), "o", markersize=7, color='r', zorder=200)
			if ylim_max < diff:
				ylim_max = diff
		i += 1

	# Plotting the blue line
	plt.plot(values, y, 'b', linewidth=4.0, zorder=180)

	plt.xticks(values, x.keys(), rotation=90, fontsize=fontsize - 5)
	plt.yticks(fontsize=fontsize)
	plt.xlabel("Experimental scenario (Workflow:Platform)", fontsize=fontsize + 1)
	plt.ylabel("% degradation from best", fontsize=fontsize + 1)

	ax.set_ylim([0.097, 1])  # top limit will be ignored anyway
	yticks = [0.1]
	ytick_labels = ["$\leq 0.1$"]

	while yticks[-1] < ylim_max:
		ytick_value = 10 * yticks[-1] + 0.0001
		ytick_label = '{}'.format(int(10 * yticks[-1]))
		yticks.append(ytick_value)
		ytick_labels.append(ytick_label)

	ax.set_yticks(yticks)
	ax.set_yticklabels(ytick_labels)

	plt.tight_layout()
	plt.savefig(output_file)
	plt.close()

	sys.stderr.write("Generated plot " + output_file + "\n")
	print("min=", y[0], "max=", y[-1])
	print("below 100%:", bisect(y, 100))
	return


#
# Helper function for generating basic algorithm "diversity" plot
##################################################################
def compute_all_percent_diffs(result_dict):
	workflows = list(workflow_index_map.keys())
	clusters = list(cluster_index_map.keys())

	algorithms = sorted(list(result_dict[workflows[0]][clusters[0]].keys()))

	percent_diff = {}
	x_labels = []
	for workflow in workflows:
		if not workflow in result_dict:
			continue
		cluster_mat = []
		for cluster in clusters:
			if not cluster in result_dict[workflow]:
				continue

			worst_single_alg_makespan = -1
			best_single_alg_makespan = -1

			for algo in algorithms:
				if algo != "us":
					if not algo in result_dict[workflow][cluster]:
						sys.stderr.write("Warning: No result for " + workflow + ":" + cluster + ":" + algo + "\n")
						continue
					makespan = result_dict[workflow][cluster][algo]
					if (best_single_alg_makespan < 0) or (best_single_alg_makespan >= makespan):
						best_single_alg_makespan = makespan
					if (worst_single_alg_makespan < 0) or (worst_single_alg_makespan <= makespan):
						worst_single_alg_makespan = makespan

			# Getting relative best-worst difference value for each workflow-cluster configuration
			config_name = "W" + str(workflow_index_map[workflow]) + ":P" + str(cluster_index_map[cluster])
			percent_diff[config_name] = (
					100.0 * (worst_single_alg_makespan - best_single_alg_makespan) / best_single_alg_makespan)

			# getting the relative difference for each algorithm in each workflow-cluster config
			relative_vals = {}
			for algo in algorithms:
				if algo != "us":
					if not algo in result_dict[workflow][cluster]:
						sys.stderr.write("Didn't find result for " + workflow + ":" + cluster + ":" + algo + "\n")
						continue
					makespan = result_dict[workflow][cluster][algo]
					relative_vals[algo] = (100 * (makespan - best_single_alg_makespan) / best_single_alg_makespan)

			percent_diff[config_name] = (percent_diff[config_name], relative_vals)

	return dict(sorted(percent_diff.items(), key=lambda item: item[1][0]))


if __name__ == "__main__":
	if len(sys.argv) != 2:
		sys.stderr.write("Usage: " + sys.argv[0] + " <version>\n")
		sys.exit(1)
	file_factor=1
	plot_path, result_dicts, workflows, clusters, best_algorithm_on_average = importData(sys.argv[1],file_factor, 2)
	sys.stdout.write("\n# BASIC ALGORITHMS PLOT\n")
	sys.stdout.write("#######################\n")
	generate_basic_algorithms_plot(plot_path, result_dicts["basic_algorithms"], best_algorithm_on_average)
