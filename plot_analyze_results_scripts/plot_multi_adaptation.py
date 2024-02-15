#!/usr/bin/env python3
from plot_utils import *


#
# Compute the multi-adaptation statistics
###############################################

def compute_multi_adaptation_statistics(multi_adaptation_result_dict):
	workflows = list(workflow_index_map.keys())
	clusters = list(cluster_index_map.keys())

	num_adapt_wins = 0
	max_adapt_improvement = 0
	ave_adapt_improvement = 0

	for workflow in workflows:
		for cluster in clusters:
			adapt_makespan = multi_adaptation_result_dict[workflow][cluster]["us_adapt"]
			no_adapt_makespan = multi_adaptation_result_dict[workflow][cluster]["us_no_adapt"]
			if adapt_makespan < no_adapt_makespan:
				num_adapt_wins += 1
				max_adapt_improvement = max(max_adapt_improvement,
											100.0 * (no_adapt_makespan - adapt_makespan) / no_adapt_makespan)
				ave_adapt_improvement += 100.0 * (no_adapt_makespan - adapt_makespan) / no_adapt_makespan
				print(100.0 * (no_adapt_makespan - adapt_makespan) / no_adapt_makespan)
				#print(workflow, cluster)
	if num_adapt_wins == 0:
		ave_adapt_improvement = 0
	else:
		ave_adapt_improvement /= num_adapt_wins

	sys.stdout.write("Multi-adaptation wins: " + str(num_adapt_wins) + "/" + str(len(workflows) * len(clusters)) + "\n")
	sys.stdout.write("Multi-adaptation max % improvement: " + str(max_adapt_improvement) + "\n")
	sys.stdout.write("Multi-adaptation ave % improvement: " + str(ave_adapt_improvement) + "\n") 	
	return


if __name__ == "__main__":
	if len(sys.argv) != 2:
		sys.stderr.write("Usage: " + sys.argv[0] + " <version>\n")
		sys.exit(1)
	file_factor=1
	plot_path, result_dicts, workflows, clusters, best_algorithm_on_average = importData(sys.argv[1], file_factor,1)
	# Compute multi-adaptation statistics
	sys.stdout.write("\n# ZERO-ERROR, MULTI-ADAPTATION STATISTICS\n")
	sys.stdout.write("#########################################\n")
	compute_multi_adaptation_statistics(result_dicts["multi_adaptation"])
