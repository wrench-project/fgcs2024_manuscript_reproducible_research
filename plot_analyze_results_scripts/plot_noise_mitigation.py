#!/usr/bin/env python3
from plot_utils import *


#
# Basic noise plot
##########################################
def plot_noise_lines(results_dict, best_algorithm_on_average):

	transMap = {}
	for noise in results_dict["mitigation"]:
		# print(results_dict["mitigation"][noise])

		noReduction = results_dict["mitigation"][noise][0.0]
		for workflow in noReduction:
			for platform in noReduction[workflow]:
				workform = "W" + workflow + ":P" + platform
				# print(workform,)
				if not workform in transMap:
					try:
						# print(noise)
						best = average(noReduction[workflow][platform]["us"])

						algs = noReduction[workflow][platform].copy()
						algs.pop("us")
						medi = sorted(algs.values())[len(algs) // 2]
						transMap[workform] = [best, dgfb(best, medi), dgfb(best,
																		   results_dict["basic_algorithms"][workflow][
																			   platform][best_algorithm_on_average])]
					except KeyError:
						break
					except ZeroDivisionError:
						break
				else:
					transMap[workform].append(dgfb(transMap[workform][0], max(noReduction[workflow][platform]["us"])))
	transpose = []
	for workform in transMap:
		transpose.append(transMap[workform])
	transpose = sorted(transpose, key=lambda x: x[2])
	# print(transpose)

	fontsize = 18
	output_file = plot_path + "noise_lines.pdf"
	f, ax1 = plt.subplots(1, 1, sharey=True, figsize=(12, 6))
	ax1.yaxis.grid()
	display_width = 0.027

	handles = []
	x_value = 0.1
	x_ticks = []
	x_ticklabels = []

	ax1.set_xticks(x_ticks)
	ax1.set_xticklabels(x_ticklabels, rotation=45, fontsize=fontsize - 2)

	ax1.set_ylabel("% makespan improvement", fontsize=fontsize)
	ax1.set_xlabel("Workflow", fontsize=fontsize)

	# Create the figure

	plt.yticks(fontsize=fontsize)
	f.tight_layout()
	colors = ["null", "black", "red", "orange", "yellow", "green", "blue", "purple", "black", "black", "black", "green",
			  "turquoise"]
	for j in [1, 2, 7]:
		line = []
		try:
			for i in range(len(transpose)):
				line.append(transpose[i][j])
			# print(j)
			if (j == 1):
				ax1.plot(range(len(line)), line, '.', linewidth=2, color=colors[j])
			else:
				ax1.plot(range(len(line)), line, '-', linewidth=2, color=colors[j])
		except:
			continue
	# ax1.plot(range(len(green)),green,  '-', linewidth=2, color="green")

	plt.savefig(output_file)
	plt.close()


#
# Violin noise plots
#############
def plot_single_noise_line(results_dict, base_noise, target_noise, best_algorithm_on_average, output_file):
	transMap = {}
	# {
	#	"W#:P#":{
	#		"best":raw sore of best algorithm,
	#		"median":dgfb of median algorithm,
	#		"boa":dgfb for best on average overall algorithm,
	#		"points":[all data points]
	#	}...
	# }

	# print(base_noise)
	# print(target_noise)
	noReduction = results_dict["noise"][base_noise][target_noise]
	noNoise = results_dict["basic_algorithms"]

	# print(cluster_index_map)

	for workflow in noNoise:
		for platform in noNoise[workflow]:
			workform = "W" + str(1 + workflow_index_map[workflow]) + ":P" + str(1 + cluster_index_map[platform])
			try:
				# print(noise)
				# print(noNoise[workflow][platform])

				best = min(noNoise[workflow][platform].values())

				algs = noNoise[workflow][platform]

				safeRemove(algs, "us")
				ranks = sorted(algs.values()).copy()
				for i in range(len(ranks)):
					ranks[i] = dgfb(best, ranks[i])
				medi = ranks[len(algs) // 2]

				transMap[workform] = {"best": best, "median": medi, "ranks": ranks,
									  "boa": dgfb(best, noNoise[workflow][platform][best_algorithm_on_average])}
				# print(noReduction[workflow][platform])
				points = noReduction[workflow][platform]["us"].copy()
				# print(points)
				for i in range(len(points)):
					points[i] = dgfb(best, points[i])
				transMap[workform]["points"] = points
			except KeyError:
				break
			except ZeroDivisionError:
				break

	# for workflow in noNoise:
	#	 for platform in noNoise[workflow]:
	#		 workform = "W" + str(1 + workflow_index_map[workflow]) + ":P" + str(1 + cluster_index_map[platform])
	#		 # print(workform + ": " + str(len(transMap[workform]["points"])))

	transpose = []
	# [
	#	{
	#		"workform":"W#:P#",
	#		"data":{
	#			"best":raw sore of best algorithm,
	#			"median":dgfb of median algorithm,
	#			"boa":dgfb for best on average overall algorithm,
	#			"points":[all data points]
	#		}
	#	}...
	# ]
	for workform in transMap:
		# transpose.append(transMap[workform])
		transpose.append({"workform": workform, "data": transMap[workform]})

	transpose = sorted(transpose, key=lambda x: x["data"]["boa"])
	# print(transpose)

	fontsize = 18
	f, ax1 = plt.subplots(1, 1, sharey=True, figsize=(12, 6))
	ax1.yaxis.grid()
	display_width = 0.027

	handles = []
	x_value = 0.1
	x_ticks = range(0, len(transMap.keys()))
	x_ticklabels = [x["workform"] for x in transpose]


	transpose = [x["data"] for x in transpose]
	# print(transpose)
	#
	#	{
	#		"best":raw sore of best algorithm,
	#		"median":dgfb of median algorithm,
	#		"boa":dgfb for best on average overall algorithm,
	#		"points":[all data points]
	#	}...
	# ]
	ax1.set_xticks(x_ticks)
	ax1.set_xticklabels(x_ticklabels, rotation=45, fontsize=fontsize - 4)

	ax1.set_ylabel("% degradation from best (dfb)", fontsize=fontsize)
	ax1.set_xlabel("Experimental scenario (Workflow:Platform)", fontsize=fontsize)

	# Create the figure

	plt.yticks(fontsize=fontsize)
	f.tight_layout()
	colors = ["null", "black", "red", "orange", "yellow", "green", "blue", "purple", "black", "black", "black", "green",
			  "turquoise"]
	line = []
	for i in range(len(transpose)):
		line.append(transpose[i]["boa"])
	# print(j)
	ax1.plot(range(len(line)), line, '-', linewidth=2, color="red")

	ymax = int(20 * int(max(line)) / 20) + 20
	ax1.set_ylim([0, ymax])

	# ax1.plot(range(len(green)),green,  '-', linewidth=2, color="green")
	pos = 0
	for i in range(len(transpose)):
		line = transpose[i]["ranks"][len(transpose[i]["ranks"]) // 2]
		if len(transpose[i]["points"]) != 0:
			plot_violin(ax1, pos, .8, transpose[i]["points"], "skyblue", 0.9)
			pos += 1
		#print("workform:",x_ticklabels[i],"average=",average(transpose[i]["points"]))
	# Legend
	legend_elements = [Line2D([0], [0], color="red", lw=2, label='One-algorithm approach'),
					   Patch(facecolor='skyblue', edgecolor='w', label='Portfolio approach')]

	plt.legend(handles=legend_elements, loc='upper center', fontsize=fontsize)

	plt.savefig(output_file)
	plt.close()
	sys.stderr.write("Generated plot '" + output_file + "'\n")


	mean_max_values = {}
	for workform in transMap:
		# print(workform)
		# print(transMap[workform]["points"])
		if len(transMap[workform]["points"]) > 0:
			mean_value = sum(transMap[workform]["points"])/len(transMap[workform]["points"])
			max_value = max(transMap[workform]["points"])
		else:
			mean_value = 0
			max_value = 0
		mean_max_values[workform] = [mean_value, max_value, transMap[workform]["points"]]
	return mean_max_values


if __name__ == "__main__":
	if len(sys.argv) != 2:
		sys.stderr.write("Usage: " + sys.argv[0] + " <version>\n")
		sys.exit(1)
	file_factor=1
	plot_path, result_dicts, workflows, clusters, best_algorithm_on_average = importData(sys.argv[1],file_factor, 1)
	# Generate the noise violin plots for all cases
	sys.stdout.write("\n# ERROR PLOTS\n")
	sys.stdout.write("#############\n")
	#start_noises = [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
	start_noises = [0.0, 0.3, 1.0]
	mean_max_values = {}
	for start_noise_index in range(0, len(start_noises)):
		start_noise = start_noises[start_noise_index]
		mean_max_values[start_noise] = {}
		for end_noise_index in range(0, start_noise_index + 1):
			end_noise = start_noises[end_noise_index]
			mean_max_values[start_noise][end_noise] = plot_single_noise_line(result_dicts, start_noise, end_noise, best_algorithm_on_average,
								   plot_path + "dfb_all_all_scenario_noise_" + str(start_noise) + "_mitigitated_noise_" + str(end_noise) + ".pdf")

	# Print some statistics needed in the paper
	mean_improved = 0
	max_improved = 0
	# print(mean_max_values[1.0][1.0])
	for workform in mean_max_values[1.0][1.0]:
		mean_delta = mean_max_values[1.0][1.0][workform][0] - mean_max_values[1.0][0.3][workform][0]
		# print(workform + ": " + str(mean_max_values[1.0][1.0][workform][0]) + " --> " + str(mean_max_values[1.0][0.3][workform][0]))
		max_delta = mean_max_values[1.0][1.0][workform][1] - mean_max_values[1.0][0.3][workform][1]
		if mean_delta > 0:
			mean_improved += 1
		if max_delta > 0:
			max_improved += 1
	print("number of scenarios for which mitigating from 1.0 to 0.3 improved the mean: " + str(mean_improved))
	print("number of scenarios for which mitigating from 1.0 to 0.3 improved the max: " + str(max_improved))

	dfb_10_10 = []
	dfb_10_03 = []
	dfb_03_03 = []
	for workform in mean_max_values[1.0][1.0]:
		dfb_10_10 += mean_max_values[1.0][1.0][workform][2]
	for workform in mean_max_values[1.0][0.3]:
		dfb_10_03 += mean_max_values[1.0][0.3][workform][2]
	for workform in mean_max_values[0.3][0.3]:
		dfb_03_03 += mean_max_values[0.3][0.3][workform][2]
	print("average dfb for 1.0-1.0: " + str(sum(dfb_10_10)/len(dfb_10_10)))
	print("average dfb for 1.0-0.3: " + str(sum(dfb_10_03)/len(dfb_10_03)))
	print("average dfb for 0.3-0.3: " + str(sum(dfb_03_03)/len(dfb_03_03)))

