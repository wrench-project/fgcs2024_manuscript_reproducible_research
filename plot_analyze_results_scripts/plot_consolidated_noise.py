#!/usr/bin/env python3
from plot_utils import *


def plot_adfb_lines(plot_path, workflow, platform, noise_lines):
	fontsize = 18
	f, ax1 = plt.subplots(1, 1, sharey=True, figsize=(12, 6))
	ax1.yaxis.grid()
	ax1.xaxis.grid()

	x_ticks = range(0, 11)
	x_ticklabels = [.0, .1, .2, .3, .4, .5, .6, .7, .8, .9, 1.0]

	ax1.set_xticks(x_ticks)
	ax1.set_xticklabels(x_ticklabels, rotation=45, fontsize=fontsize - 2)

	ax1.set_ylabel("% degradation from best (dfb)", fontsize=fontsize)
	ax1.set_xlabel("Mitigated simulation error ($e'$)", fontsize=fontsize)
	plt.xlim([0, 11.1])
	ax1.invert_xaxis()

	if workflow == "all_workflows.json":
		x_text_offset = {}
		y_text_offset = {}
		for start_noise in noise_lines:
			x_text_offset[start_noise] = -0.1
			y_text_offset[start_noise] = -0.15

		y_text_offset[0.7] = -0.10
		y_text_offset[0.5] = -0.20
		y_text_offset[0.2] = -0.15
		y_text_offset[0.1] = -0.4

	# Sort noise_lines by decreasing start noise
	for start_noise in reversed(noise_lines):
		ax1.plot(range(0, len(noise_lines[start_noise])), noise_lines[start_noise], label="e = " + str(start_noise),
				 linewidth=3)
		if workflow == "all_workflows.json":
			ax1.text(x_text_offset[start_noise] + len(noise_lines[start_noise]),
					 y_text_offset[start_noise] + noise_lines[start_noise][-1], "$e=" + str(start_noise) + "$",
					 fontsize=fontsize - 1)

	plt.yticks(fontsize=fontsize)
	plt.legend(fontsize=fontsize, ncol=2)

	plt.tight_layout()

	filename = plot_path + "dfb_vs_mitigated_error_" + workflow.split(".")[0].split("-")[0] + "_P" + str(
		len(platform.split(","))) + ".pdf"
	plt.savefig(filename)
	plt.close()
	sys.stderr.write("Generated plot " + filename + "\n")


if __name__ == "__main__":
	if len(sys.argv) != 2:
		sys.stderr.write("Usage: " + sys.argv[0] + " <version>\n")
		sys.exit(1)
	file_factor=1
	plot_path, result_dicts, workflows, clusters, best_algorithm_on_average = importData(sys.argv[1],file_factor, 1)
	# Plot adfb line results per workflow / platform
	sys.stdout.write("\n# AVE. DFB PLOTS PER WORKFLOW / PLATFORM\n")
	sys.stdout.write("########################################\n")
	start_noises = [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
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
			plot_adfb_lines(plot_path, workflow, cluster, noise_lines)
