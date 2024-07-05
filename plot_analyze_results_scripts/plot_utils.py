#!/usr/bin/env python3
import sys
import ast
import matplotlib.pyplot as plt
from matplotlib.pyplot import figure
import random
import numpy as np
from matplotlib.patches import Patch
from matplotlib.lines import Line2D
from pathlib import Path

# index to name maps
workflow_index_map = {}
cluster_index_map = {}

#
# Helper function to compute dfb
######################################
def dgfb(best, target):
	return round(100.0 * (target - best) / best,2)


#
# Helper function, because removing a key that doesnt exist is apparently an error
######################################
def safeRemove(map, key):
	try:
		map.pop(key)
	except:
		pass
	return map


#
# Helper function because APPARENTLY average ISNT a standard function like sum or len
####################################
def average(array):
	if len(array) == 0:
		return 0
	return sum(array) / len(array)


#
# Helper that plots violin plots
######################################	
def plot_violin(axis, position, width, data, color, alpha):
	# color = matplotlib.colors.to_rgba("red", alpha)
	v = axis.violinplot(data, positions=[position], widths=[width], showmeans=True)
	for pc in v['bodies']:
		pc.set_color(color)
		pc.set_alpha(alpha)
	bar_color = "black"
	bar_linewidth = 1.15
	v['cmaxes'].set_color(bar_color)
	v['cmaxes'].set_linewidth(bar_linewidth)
	v['cmins'].set_color(bar_color)
	v['cmins'].set_linewidth(bar_linewidth)
	v['cbars'].set_color(bar_color)
	v['cbars'].set_linewidth(bar_linewidth)
	v['cmeans'].set_color(bar_color)
	v['cmeans'].set_linewidth(bar_linewidth + 0.5)
	return v


#
# Print the DFB statistics for basic algorithms
###############################################
def print_dfb_statistics(results, verbosity=2):
	dfb = {}
	worst_dfb = {}

	algorithms = set({})

	num_complete_scenarios = 0
	num_total_scenarios = 0
	for workflow in results:
		for cluster in results[workflow]:
			num_total_scenarios += 1
			makespans = {}
			for algo in results[workflow][cluster]:
				makespans[algo] = results[workflow][cluster][algo]

			if len(makespans) == 0:
				continue

			best = min(makespans.values())
			for algo, makespan in makespans.items():
				algorithms.add(algo)
				dfb_value = 100 * (makespan - best) / best
				if algo not in dfb:
					dfb[algo] = dfb_value
				else:
					dfb[algo] += dfb_value
				if algo not in worst_dfb:
					worst_dfb[algo] = dfb_value
				else:
					if worst_dfb[algo] < dfb_value:
						worst_dfb[algo] = dfb_value

			num_complete_scenarios += 1
	if verbosity > 0:
		sys.stdout.write("\nSorted DFB results for " + str(num_complete_scenarios) + "/" +
						 str(num_total_scenarios) + " scenarios:\n")

	dfb = {algo: (value / num_complete_scenarios) for algo, value in dfb.items()}

	dfb = dict(sorted(dfb.items(), key=lambda x: x[1]))
	count=0
	if verbosity > 1:
		for algo, avg_dfb in dfb.items():
			if count==int(len(dfb)/2):
				sys.stdout.write("Median: ")
			sys.stdout.write(algo + "\n")
			sys.stdout.write("  - average fdb: " + str(round(avg_dfb, 2)) + "\n")
			sys.stdout.write("  - worst   dfb: " + str(round(worst_dfb[algo], 2)) + "\n")
			count+=1
	return [x for x in dfb.items()][0][0]  # Return best algorithm on average


def compute_adfb(results_dict, workflow, platform, base_noise, target_noise):
	noReduction = results_dict["noise_mitigation"][base_noise][target_noise][workflow]
	noNoise = results_dict["basic_algorithms"][workflow]

	# print(workflow + " base noise: " + str(base_noise) + "  target noise: " + str(target_noise))
	ave = 0
	count = 0
	for platform in [platform]:
		try:
			points = noReduction[platform]["us"].copy()

			algs = noNoise[platform]
			safeRemove(algs, "us")
			best = min(noNoise[platform].values())

			for i in range(len(points)):
				ave += dgfb(best, points[i])
			count += len(points)

		except KeyError:
			break
		except ZeroDivisionError:
			break

	if count == 0:
		return None

	# print("	 " + str(ave / count))
	return ave / count


#
# Helper function, imports all the data and returns the result_dict, workflows , and clusters
###################################
def importData(version, file_factor, verbosity=2):
	plot_path = "plots_" + version + "/"

	# Read extracted files in to a dictionary of results
	extracted_files = {"basic_algorithms": "../extract_scripts/basic_algorithms_extracted_results_" + version + ".dict",
					   "multi_adaptation": "../extract_scripts/multi_adaptation_results_" + version + ".dict",
					   "noise": "../extract_scripts/noise_extracted_results_" + version + ".dict",
					   "noise_mitigation": "../extract_scripts/noise_mitigation_extracted_results_" + version + ".dict",
					   "no_contention_yes_amdahl_noise": "../extract_scripts/no_contention_yes_amdahl_noise_extracted_results_"+version+".dict",
					   "no_contention_no_amdahl_noise": "../extract_scripts/no_contention_no_amdahl_noise_extracted_results_"+version+".dict",
					   "yes_contention_no_amdahl_noise": "../extract_scripts/yes_contention_no_amdahl_noise_extracted_results_"+version+".dict"
					   }
	result_dicts = {}
	for f in extracted_files:
		try:
			print(extracted_files[f])
			file = open(extracted_files[f], "r")
		except OSError:
			sys.stderr.write("Can't find extracted result file '" + extracted_files[f] +
							 "'. Start Mongo and run the extract_all_results.py script first!\n")
			sys.exit(1)
		contents = file.read()
		allResults=ast.literal_eval(contents)
		result_dicts[f] = allResults[file_factor]

	# Identify the workflows and the clusters, in sorted lists
	workflows = sorted(result_dicts["basic_algorithms"].keys())  # sorted lexicographically
	clusters = sorted(result_dicts["basic_algorithms"][workflows[0]].keys(), key=lambda x: len(x))  # sorted by length

	# Create workflows and clusters numbering maps
	for idx in range(0, len(workflows)):
		workflow_index_map[workflows[idx]] = idx
	for idx in range(0, len(clusters)):
		cluster_index_map[clusters[idx]] = idx
	# Print dfb statistics and identify best-on-average algorithm
	if (verbosity > 1):
		sys.stdout.write("\n# BASIC ALGORITHM DFB STATISTICS\n")
		sys.stdout.write("################################\n")

	best_algorithm_on_average = print_dfb_statistics(result_dicts["basic_algorithms"], verbosity)
	if verbosity > 0:
		sys.stdout.write("\nBest algorithm on average = " + best_algorithm_on_average + "\n")

	Path(plot_path).mkdir(parents=True, exist_ok=True)
	return plot_path, result_dicts, workflows, clusters, best_algorithm_on_average
