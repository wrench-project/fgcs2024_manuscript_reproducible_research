#!/usr/bin/env python3
from plot_utils import *


def plot_no_mitigation(plot_path, results_dict, best_algorithm_on_average):
	# (Re) Compute the dfb of the best_algorithm_on_average
	noNoise = results_dict["basic_algorithms"]
	best_algorithm_on_average_ave_dfb = 0
	best_algorithm_on_average_ave_dfb_count = 0

	for workflow in noNoise:
		for platform in noNoise[workflow]:
			algs = noNoise[workflow][platform]
			best = min(algs.values())
			best_algorithm_on_average_ave_dfb += dgfb(best, noNoise[workflow][platform][best_algorithm_on_average])
			best_algorithm_on_average_ave_dfb_count += 1

	best_algorithm_on_average_ave_dfb /= best_algorithm_on_average_ave_dfb_count

	# Compute our dfb for all noises
	averages = []
	flats = {}
	maxima = []
	minima = []
	errors = []
	for base_noise in results_dict["noise"]:
		if base_noise == 0.0:
			continue
		# todo rework for point distributions
		transMap = {}

		noReduction = results_dict["noise"][base_noise][base_noise]

		for workflow in noNoise:
			for platform in noNoise[workflow]:
				workform = "W" + str(workflow_index_map[workflow]) + ":P" + str(cluster_index_map[platform])
				# print(workform)
				try:
					# print(noise)
					# print(noNoise[workflow][platform])
					algs = noNoise[workflow][platform]

					safeRemove(algs, "us")
					best = min(algs.values())

					transMap[workform] = []
					points = noReduction[workflow][platform]["us"].copy()
					for i in range(len(points)):
						points[i] = dgfb(best, points[i])
					# print(points)
					transMap[workform] = points
				except KeyError:
					break
				except ZeroDivisionError:
					break

		flats[base_noise] = []
		for workform in transMap:
			for point in transMap[workform]:
				flats[base_noise].append(point)
		std_error = np.std(flats[base_noise], ddof=1) / np.sqrt(len(flats[base_noise]))
		average = sum(flats[base_noise]) / len(flats[base_noise])
		averages.append(average)
		maxima.append(max(flats[base_noise]))
		minima.append(min(flats[base_noise]))
		errors.append(std_error)

	fontsize = 18
	f, ax1 = plt.subplots(1, 1, sharey=True, figsize=(12, 4))
	ax1.yaxis.grid()
	display_width = 0.027

	handles = []
	x_value = 0.1
	x_ticks = range(0, 10)
	x_ticklabels = [.1, .2, .3, .4, .5, .6, .7, .8, .9, 1.0]

	ax1.set_xticks(x_ticks)
	ax1.set_xticklabels(x_ticklabels, rotation=45, fontsize=fontsize - 2)

	ax1.set_ylabel("% degradation from best (dfb)", fontsize=fontsize-3)
	ax1.set_xlabel("Simulation error magnitude ($e$)", fontsize=fontsize)
	ax1.invert_xaxis()
	ax1.plot([x_ticks[0]-0.5, x_ticks[-1]+0.5], [best_algorithm_on_average_ave_dfb, best_algorithm_on_average_ave_dfb], 'r-')
	ax1.plot(range(0, len(averages)), averages, 'b-', linewidth=2)

	pos = x_ticks[0]
	for base_noise in flats:
		plot_violin(ax1, pos, 0.6, flats[base_noise], "skyblue", 0.9)
		percentage_above = 100.0 * len([x for x in flats[base_noise] if x > best_algorithm_on_average_ave_dfb]) / len(flats[base_noise])
		plt.text(pos -0.05, best_algorithm_on_average_ave_dfb + 0.3, "{:.2f}".format(round(percentage_above, 2)) + "%", fontsize=fontsize-3)
		plt.text(pos -0.05, best_algorithm_on_average_ave_dfb - 0.9, "{:.2f}".format(round(100 - percentage_above, 2)) + "%", fontsize=fontsize-3)
		pos += 1

	#	ax1.errorbar(range(0, len(averages)), averages, yerr=errors, capsize=10)
	# Create the figure

	plt.ylim([0,16])

	plt.yticks(fontsize=fontsize)
	f.tight_layout()

	output_filename = plot_path + "dfb_vs_error_full.pdf"
	plt.savefig(output_filename)
	plt.close()
	sys.stderr.write("Generated plot '" + output_filename + "'\n")


if __name__ == "__main__":
	if len(sys.argv) != 2:
		sys.stderr.write("Usage: " + sys.argv[0] + " <version>\n")
		sys.exit(1)
	file_factor=1
	plot_path, result_dicts, workflows, clusters, best_algorithm_on_average = importData(sys.argv[1],file_factor, 1)

	# No mitigation results
	sys.stdout.write("\n# NO MITIGATION PLOT \n")
	sys.stdout.write("#######################\n")
	plot_no_mitigation(plot_path, result_dicts, best_algorithm_on_average)
