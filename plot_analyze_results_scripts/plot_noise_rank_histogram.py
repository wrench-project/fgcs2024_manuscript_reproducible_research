#!/usr/bin/env python3
from plot_utils import *
from bisect import bisect_left


#
# Noise Rank Histograms
#############
def plot_rank_histograms(results_dict, base_noise, target_noise, output_file):
	histogram = [0] * 49
	total = 0
	# print(base_noise)
	# print(target_noise)
	noReduction = results_dict["noise"][base_noise][target_noise]
	noNoise = results_dict["basic_algorithms"]

	for workflow in noNoise:
		for platform in noNoise[workflow]:

			try:
				# print(noise)
				# print(noNoise[workflow][platform])
					
				best = min(noNoise[workflow][platform].values())

				algs = noNoise[workflow][platform]

				safeRemove(algs, "us")
				ranks = sorted(algs.values()).copy()

				for i in range(len(ranks)):
					ranks[i] = dgfb(best, ranks[i])

				points = noReduction[workflow][platform]["us"]
				for i in range(len(points)):
					target = dgfb(best, points[i])
					rank = bisect_left(ranks, target)
					# print(rank,len(ranks))
					histogram[rank] += 1
					total += 1
				

			except KeyError:
				break
			except ZeroDivisionError:
				break

	for i in range(len(histogram)):
		histogram[i] /= total

	print(histogram)
	fontsize = 18
	f, ax1 = plt.subplots(1, 1, sharey=True, figsize=(12, 6))
	# ax1.yaxis.grid()
	# display_width = 0.027

	# handles = []
	# y_value = 1
	# y_ticks = range(0, len(transMap.keys()))
	# y_ticklabels = [x["workform"] for x in transpose]

	# ax1.set_yticks(y_ticks)
	# ax1.set_yticklabels(x_ticklabels, rotation=45, fontsize=fontsize - 4)

	# ax1.set_ylabel("% degradation from best (dfb)", fontsize=fontsize)
	# ax1.set_xlabel("Experimental scenario (Workflow:Platform)", fontsize=fontsize)

	# Create the figure
	plt.ylim(0, 0.7)
	ax1.bar(range(len(histogram)), histogram)
	plt.yticks(fontsize=fontsize)
	f.tight_layout()

	# plt.legend(handles=legend_elements, loc='upper center', fontsize=fontsize)
	# output_file=plot_path+"rank_histograms.pdf"
	plt.savefig(output_file)
	plt.close()
	sys.stderr.write("Generated plot '" + output_file + "'\n")


def plot_cumulative_rank_histograms(plot_path, results_dict, noises):
	output_file = plot_path + "algorithm_rank_cdfs.pdf"
	histograms = []

	# print(base_noise)
	# print(target_noise)
	noNoise = results_dict["basic_algorithms"]
	for base_noise in noises:
		histogram = [0] * 48
		total = 0
		noReduction = results_dict["noise"][base_noise][base_noise]

		for workflow in noNoise:
			for platform in noNoise[workflow]:

				try:
					# print(noise)
					# print(noNoise[workflow][platform])

					best = min(noNoise[workflow][platform].values())

					algs = noNoise[workflow][platform]

					safeRemove(algs, "us")
					ranks = sorted(algs.values()).copy()

					for i in range(len(ranks)):
						ranks[i] = dgfb(best, ranks[i])

					points = noReduction[workflow][platform]["us"]
					for i in range(len(points)):
						target = dgfb(best, points[i])
						rank = bisect_left(ranks, target)
						# print(rank,len(ranks))
						histogram[rank] += 1
						total += 1
					#if(base_noise==0):
					#	print(workflow,platform,rank,target)
					#	if(rank!=0):
					#		print(ranks)
				except KeyError:
					break
				except ZeroDivisionError:
					break
		for i in range(len(histogram)):
			histogram[i] /= total
		total = 0
		# print(histogram)
		for i in range(len(histogram)):
			total += histogram[i]
			histogram[i] = total
		histograms.append(histogram)

	fontsize = 18
	f, ax1 = plt.subplots(1, 1, sharey=True, figsize=(12, 6))
	# ax1.yaxis.grid()
	# display_width = 0.027

	# handles = []
	y_value = 1
	x_ticks = range(0, len(histograms[0]), 5)
	# y_ticklabels = [x["workform"] for x in transpose]

	ax1.set_xticks(x_ticks)
	# ax1.set_yticklabels(x_ticklabels, rotation=45, fontsize=fontsize - 4)

	ax1.set_ylabel("Percentage of Scenarios", fontsize=fontsize)
	ax1.set_xlabel("Selected algorithm rank", fontsize=fontsize)
	# plt.yscale("logit")
	# Create the figure
	plt.ylim(50, 101)
	plt.xlim(-1, 47)
	plt.grid()
	for i in range(len(histograms)):
		histogram = histograms[i]
		ax1.plot(range(len(histogram)), [x * 100 for x in histogram], label="e=" + str(noises[i]), linewidth=2)
	plt.yticks(fontsize=fontsize)
	plt.legend(fontsize=fontsize+1)
	f.tight_layout()

	# plt.legend(handles=legend_elements, loc='upper center', fontsize=fontsize)
	# output_file=plot_path+"rank_histograms.pdf"
	plt.savefig(output_file)
	plt.close()
	sys.stderr.write("Generated plot '" + output_file + "'\n")


if __name__ == "__main__":
	if len(sys.argv) != 2:
		sys.stderr.write("Usage: " + sys.argv[0] + " <version>\n")
		sys.exit(1)
	file_factor=1
	plot_path, result_dicts, workflows, clusters, best_algorithm_on_average = importData(sys.argv[1],file_factor, 1)
	# Generate the noise violin plots for all cases
	sys.stdout.write("\n# RANK HISTOGRAM PLOTS\n")
	sys.stdout.write("#############\n")
	start_noises = [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
	plot_cumulative_rank_histograms(plot_path, result_dicts, start_noises)
