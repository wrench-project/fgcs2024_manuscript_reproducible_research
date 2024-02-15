#!/usr/bin/env python3
from plot_utils import *

# the following code roughly translates
# import ./*.py 
import os

for module in os.listdir(os.path.dirname(os.path.abspath(__file__))):
	if module == __file__ or module[-3:] != '.py' or ' ' in module:
		continue
	exec("import " + module[:-3])
del module


def main():
	if len(sys.argv) != 2:
		sys.stderr.write("Usage: " + sys.argv[0] + " <version>\n")
		sys.exit(1)
	file_factors=[1]
	file_factor=1
	plot_path, result_dicts, workflows, clusters, best_algorithm_on_average = importData(sys.argv[1],file_factor, 2)

	# Generate basic algorithms plot
	sys.stderr.write("\n# BASIC ALGORITHMS PLOT\n")
	sys.stderr.write("#######################\n")
	plot_basic_algorithms.generate_basic_algorithms_plot(plot_path, result_dicts["basic_algorithms"], best_algorithm_on_average)

	# Compute multi-adaptation statistics
	#sys.stdout.write("\n# ZERO-ERROR, MULTI-ADAPTATION STATISTICS\n")
	#sys.stdout.write("#########################################\n")
	#compute_multi_adaptation_statistics(result_dicts["multi_adaptation"])
	# broken by current data
	
	# Generate the noise violin plots for all cases
	sys.stderr.write("\n# ERROR PLOTS\n")
	sys.stderr.write("#############\n")
	start_noises = [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
	for start_noise_index in range(0, len(start_noises)):
		start_noise = start_noises[start_noise_index]
		for end_noise_index in range(0, start_noise_index + 1):
			end_noise = start_noises[end_noise_index]
			plot_noise_mitigation.plot_single_noise_line(result_dicts, start_noise, end_noise, best_algorithm_on_average,
								   plot_path + "dfb_vs_scenario_noise_" + str(start_noise) + "_mitigated_noise_" + str(end_noise) + ".pdf")


	# Plot adfb line results per workflow / platform
	sys.stderr.write("\n# AVE. DFB PLOTS PER WORKFLOW / PLATFORM\n")
	sys.stderr.write("########################################\n")
	for workflow in workflows:
		for cluster in clusters:
			noise_lines = {}
			for start_noise_index in range(0, len(start_noises)):
				start_noise = start_noises[start_noise_index]
				if start_noise <= 0.0:
					continue
				line = []
				for end_noise_index in range(0, start_noise_index + 1):
					end_noise = start_noises[end_noise_index]
					adfb = compute_adfb(result_dicts, workflow, cluster, start_noise, end_noise)
					line.append(adfb)
				noise_lines[start_noise] = line
			plot_consolidated_noise.plot_adfb_lines(plot_path, workflow, cluster, noise_lines)

	# No mitigation results
	sys.stderr.write("\n# NO MITIGATION PLOT \n")
	sys.stderr.write("#######################\n")
	plot_no_mitigation.plot_no_mitigation(plot_path, result_dicts, best_algorithm_on_average)

	# Rank histogram plot
	sys.stderr.write("\n# RANK HISTOGRAM PLOTS\n")
	sys.stderr.write("########################\n")
	start_noises = [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
	plot_noise_rank_histogram.plot_cumulative_rank_histograms(plot_path, result_dicts, start_noises)

	# Sophistication plot
	sys.stderr.write("\n# SOPHISTICATION PLOTS \n")
	sys.stderr.write("########################\n")

	# plot_path, result_dicts, workflows, clusters, best_algorithm_on_average = \
	# importData(sys.argv[1], file_factor=1, verbosity=1)

	platforms = clusters[0:3]
	plot_simulator_sophistication.plot_simulator_sophistication_dfbs(plot_path, "ALL", result_dicts, workflows, clusters)

	for workflow in workflows:
		plot_simulator_sophistication.plot_simulator_sophistication_dfbs(plot_path, workflow.split("-")[0], result_dicts, [workflow], platforms)


# MAIN
if __name__ == "__main__":
	try:
		main()
	except KeyboardInterrupt:
		pass #dont throw massive error on ctrl+c
