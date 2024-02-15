#!/usr/bin/env python3
import random
from os.path import exists
import glob
import sys
import json
from pymongo import MongoClient


def connect_to_mongo(version, mongo_url):
	# Setup Mongo
	try:
		mongo_client = MongoClient(host=mongo_url, serverSelectionTimeoutMS=1000)
		mydb = mongo_client["scheduling_with_simulation"]
		collection = mydb["results_" + version]
	except:
		sys.stderr.write("Cannot connect to MONGO\n")
		sys.exit(1)
	return collection


def write_results_to_file(filename, data):
	f = open(filename, "w")
	f.write(str(data) + "\n")
	f.close()
	print("Extracted result dictionary written to file " + filename)


def main():
	if len(sys.argv) != 3:
		sys.stderr.write("Usage: " + sys.argv[0] + " <version> <mongo url>\n")
		sys.stderr.write("  For instance: " + sys.argv[0] + " fgcs2024 mongodb://localhost:27017\n")
		sys.exit(1)

	version = sys.argv[1]
	mongo_url = sys.argv[2]

	try:
		collection = connect_to_mongo(version, mongo_url)
	except:
		sys.stderr.write("Couldn't connect\n")
		sys.exit(1)
	# Get values for fields in database
	workflows = set()
	clusters = set()
	noises = set()
	noise_reductions = set()
	file_factors = set()
	cursor = collection.find({})
	for doc in cursor:
		workflows.add(doc["workflow"])
		clusters.add(doc["clusters"])
		noises.add(doc["simulation_noise"])
		noise_reductions.add(doc["simulation_noise_reduction"])
		file_factors.add(doc["file_size_factor"])
		
		
	workflows = sorted(list(workflows))
	clusters = sorted(list(clusters))
	noises = sorted(list(noises))
	noise_reductions = sorted(list(noise_reductions))
	file_factors = sorted(list(file_factors))

	#if False:
	# BASIC ALGORITHMS RESULTS
	############################################
	sys.stderr.write("Extracting 'basic_algorithms' results...\n")
	file_factor_dict={}
	for file_factor in file_factors:
		results = {}
		print("File Factor: " + str(file_factor))

		for workflow in workflows:
			results[workflow] = {}

			for cluster in clusters:
				results[workflow][cluster] = {}

				cursor = collection.find({"file_size_factor":file_factor,"clusters": cluster, "workflow": workflow,"no_contention":False,"no_contention_in_speculative_executions":False,"no_amdahl_in_speculative_executions":False})
				us_makespans = []
				for doc in cursor:
					# print(doc)
					is_us = (len(doc["task_selection_schemes"].split(",")) > 1) or (
							len(doc["cluster_selection_schemes"].split(",")) > 1) or (
									len(doc["core_selection_schemes"].split(",")) > 1)
					# print(is_us)
					if not is_us:
						alg_name = doc["task_selection_schemes"] + "/" + doc["cluster_selection_schemes"] + "/" + doc[
							"core_selection_schemes"]
						results[workflow][cluster][alg_name] = doc["makespan"]
		file_factor_dict[file_factor]=results
	write_results_to_file("basic_algorithms_extracted_results_"+version+".dict", file_factor_dict)

	# MULTI-ADAPTION RESULTS
	############################################
	sys.stderr.write("Extracting 'multi_adaptation' results...\n")
	file_factor_dict={}
	for file_factor in file_factors:
		results = {}
		print("File Factor: " + str(file_factor))

		for workflow in workflows:
			results[workflow] = {}

			for cluster in clusters:
				results[workflow][cluster] = {}

				cursor = collection.find({"file_size_factor":file_factor,"clusters": cluster, "workflow": workflow,"no_contention":False,"no_contention_in_speculative_executions":False,"no_amdahl_in_speculative_executions":False})
				us_makespans = []
				for doc in cursor:
					if doc["simulation_noise"] > 0.0:
						continue
					is_us = (len(doc["task_selection_schemes"].split(",")) > 1) or (
							len(doc["cluster_selection_schemes"].split(",")) > 1) or (
									len(doc["core_selection_schemes"].split(",")) > 1)
					# print(is_us)
					if is_us:
						if doc["disable_adaptation_if_noise_has_not_changed"]:
							results[workflow][cluster]["us_no_adapt"] = doc["makespan"]
						else:
							results[workflow][cluster]["us_adapt"] = doc["makespan"]
		file_factor_dict[file_factor]=results
	write_results_to_file("multi_adaptation_results_"+version+".dict", file_factor_dict)

	# NOISE RESULTS
	############################################
	sys.stderr.write("Extracting 'noise' results...\n")
	file_factor_dict={}
	for file_factor in file_factors:
		results = {}
		print("File Factor: " + str(file_factor))

		for noise in noises:
			print("NOISE: " + str(noise))
			results[noise] = {}

			for noise_reduction in noise_reductions:

				if noise_reduction > noise:
					continue

				target_noise = (int(10 * noise) - int(10 * noise_reduction)) / 10
				results[noise][target_noise] = {}

				for workflow in workflows:
					# print("	WORKFLOW: " + workflow)
					results[noise][target_noise][workflow] = {}

					for cluster in clusters:
						# print("	  PLATFORMS: "+cluster)
						results[noise][target_noise][workflow][cluster] = {}

						cursor = collection.find({"file_size_factor":file_factor,"clusters": cluster, "workflow": workflow,"no_contention":False,"no_contention_in_speculative_executions":False,"no_amdahl_in_speculative_executions":False})
						us_makespans = []
						for doc in cursor:
							if (noise_reduction == 0.0) and (doc["disable_adaptation_if_noise_has_not_changed"] == False):
								continue
							is_us = (len(doc["task_selection_schemes"].split(",")) > 1) or (
									len(doc["cluster_selection_schemes"].split(",")) > 1) or (
											len(doc["core_selection_schemes"].split(",")) > 1)
							if not is_us:
								alg_name = doc["task_selection_schemes"] + "/" + doc["cluster_selection_schemes"] + "/" + \
										   doc["core_selection_schemes"]
								results[noise][target_noise][workflow][cluster][alg_name] = doc["makespan"]
							else:
								if (doc["simulation_noise"] == noise) and (
										doc["simulation_noise_reduction"] == noise_reduction):
									us_makespans.append(doc["makespan"])
						results[noise][target_noise][workflow][cluster]["us"] = us_makespans
		file_factor_dict[file_factor]=results
	write_results_to_file("noise_extracted_results_"+version+".dict", file_factor_dict)

	# NOISE MITIGATION RESULTS
	############################################
	sys.stderr.write("Extracting 'noise mitigation' results...\n")
	file_factor_dict={}
	for file_factor in file_factors:
		results = {}
		print("File Factor: " + str(file_factor))

		for noise in noises:
			print("NOISE: " + str(noise))
			results[noise] = {}

			for noise_reduction in noise_reductions:

				if noise_reduction > noise:
					continue

				target_noise = (int(10 * noise) - int(10 * noise_reduction)) / 10
				results[noise][target_noise] = {}

				for workflow in workflows:
					# print("	WORKFLOW: " + workflow)
					results[noise][target_noise][workflow] = {}

					for cluster in clusters:
						# print("	  PLATFORMS: "+cluster)
						results[noise][target_noise][workflow][cluster] = {}

						cursor = collection.find({"file_size_factor":file_factor,"clusters": cluster, "workflow": workflow,"no_contention":False,"no_contention_in_speculative_executions":False,"no_amdahl_in_speculative_executions":False})
						us_makespans = []
						for doc in cursor:
							if noise_reduction == 0.0:
								if doc["disable_adaptation_if_noise_has_not_changed"]:
									continue
							is_us = (len(doc["task_selection_schemes"].split(",")) > 1) or (
									len(doc["cluster_selection_schemes"].split(",")) > 1) or (
											len(doc["core_selection_schemes"].split(",")) > 1)
							if not is_us:
								alg_name = doc["task_selection_schemes"] + "/" + doc["cluster_selection_schemes"] + "/" + \
										   doc["core_selection_schemes"]
								results[noise][target_noise][workflow][cluster][alg_name] = doc["makespan"]
							else:
								if (doc["simulation_noise"] == noise) and (
										doc["simulation_noise_reduction"] == noise_reduction):
									us_makespans.append(doc["makespan"])
						results[noise][target_noise][workflow][cluster]["us"] = us_makespans
		file_factor_dict[file_factor]=results
	write_results_to_file("noise_mitigation_extracted_results_"+version+".dict", file_factor_dict)

	# IDEAL NO CONTENTION RESULTS
	############################################
	sys.stderr.write("Extracting 'ideal no contention' results...\n")
	file_factor_dict={}
	for file_factor in file_factors:
		results = {}
		print("File Factor: " + str(file_factor))

		for workflow in workflows:
			# print("	WORKFLOW: " + workflow)
			results[workflow] = {}

			for cluster in clusters:
				# print("	  PLATFORMS: "+cluster)
				results[workflow][cluster] = {}

				cursor = collection.find({"file_size_factor":file_factor,"clusters": cluster, "workflow": workflow,"no_contention":True})
				us_makespans = []
				for doc in cursor:
					
						alg_name = doc["task_selection_schemes"] + "/" + doc["cluster_selection_schemes"] + "/" + \
								   doc["core_selection_schemes"]
						results[workflow][cluster][alg_name] = doc["makespan"]

		file_factor_dict[file_factor]=results

	write_results_to_file("no_contention_ideal_extracted_results_"+version+".dict", file_factor_dict)
	
	# CONTENTION NOISE RESULTS
	############################################
	sys.stderr.write("Extracting 'contention noise' results...\n")
	file_factor_dict={}
	for file_factor in file_factors:
		results = {}
		print("File Factor: " + str(file_factor))
		for noise in noises:
			print("NOISE: " + str(noise))
			results[noise] = {}

			for noise_reduction in noise_reductions:

				if noise_reduction > noise:
					continue

				target_noise = (int(10 * noise) - int(10 * noise_reduction)) / 10
				results[noise][target_noise] = {}

				for workflow in workflows:
					# print("	WORKFLOW: " + workflow)
					results[noise][target_noise][workflow] = {}

					for cluster in clusters:
						# print("	  PLATFORMS: "+cluster)
						results[noise][target_noise][workflow][cluster] = {}

						cursor = collection.find({"file_size_factor":file_factor,"clusters": cluster, "workflow": workflow,"no_contention":False,"no_contention_in_speculative_executions":True,"no_amdahl_in_speculative_executions":False})
						us_makespans = []
						for doc in cursor:
							if (noise_reduction == 0.0) and (doc["disable_adaptation_if_noise_has_not_changed"] == False):
								continue
							is_us = (len(doc["task_selection_schemes"].split(",")) > 1) or (
									len(doc["cluster_selection_schemes"].split(",")) > 1) or (
											len(doc["core_selection_schemes"].split(",")) > 1)
							if not is_us:
								alg_name = doc["task_selection_schemes"] + "/" + doc["cluster_selection_schemes"] + "/" + \
										   doc["core_selection_schemes"]
								results[noise][target_noise][workflow][cluster][alg_name] = doc["makespan"]
							else:
								if (doc["simulation_noise"] == noise) and (
										doc["simulation_noise_reduction"] == noise_reduction):
									us_makespans.append(doc["makespan"])
						results[noise][target_noise][workflow][cluster]["us"] = us_makespans
		file_factor_dict[file_factor]=results
	write_results_to_file("no_contention_yes_amdahl_noise_extracted_results_"+version+".dict", file_factor_dict)
	
	# CONTENTION AHMDAL NOISE RESULTS
	############################################
	sys.stderr.write("Extracting 'contention amdahl noise' results...\n")
	file_factor_dict={}
	for file_factor in file_factors:
		results = {}
		print("File Factor: " + str(file_factor))
		for noise in noises:
			print("NOISE: " + str(noise))
			results[noise] = {}

			for noise_reduction in noise_reductions:

				if noise_reduction > noise:
					continue

				target_noise = (int(10 * noise) - int(10 * noise_reduction)) / 10
				results[noise][target_noise] = {}

				for workflow in workflows:
					# print("	WORKFLOW: " + workflow)
					results[noise][target_noise][workflow] = {}

					for cluster in clusters:
						# print("	  PLATFORMS: "+cluster)
						results[noise][target_noise][workflow][cluster] = {}

						cursor = collection.find({"file_size_factor":file_factor,"clusters": cluster, "workflow": workflow,"no_contention":False,"no_contention_in_speculative_executions":True,"no_amdahl_in_speculative_executions":True})
						us_makespans = []
						for doc in cursor:
							if (noise_reduction == 0.0) and (doc["disable_adaptation_if_noise_has_not_changed"] == False):
								continue
							is_us = (len(doc["task_selection_schemes"].split(",")) > 1) or (
									len(doc["cluster_selection_schemes"].split(",")) > 1) or (
											len(doc["core_selection_schemes"].split(",")) > 1)
							if not is_us:
								alg_name = doc["task_selection_schemes"] + "/" + doc["cluster_selection_schemes"] + "/" + \
										   doc["core_selection_schemes"]
								results[noise][target_noise][workflow][cluster][alg_name] = doc["makespan"]
							else:
								if (doc["simulation_noise"] == noise) and (
										doc["simulation_noise_reduction"] == noise_reduction):
									us_makespans.append(doc["makespan"])
						results[noise][target_noise][workflow][cluster]["us"] = us_makespans
		file_factor_dict[file_factor]=results
	write_results_to_file("no_contention_no_amdahl_noise_extracted_results_"+version+".dict", file_factor_dict)

	sys.stderr.write("Extracting 'amdahl noise' results...\n")
	file_factor_dict={}
	for file_factor in file_factors:
		results = {}
		print("File Factor: " + str(file_factor))
		for noise in noises:
			print("NOISE: " + str(noise))
			results[noise] = {}

			for noise_reduction in noise_reductions:

				if noise_reduction > noise:
					continue

				target_noise = (int(10 * noise) - int(10 * noise_reduction)) / 10
				results[noise][target_noise] = {}

				for workflow in workflows:
					# print("	WORKFLOW: " + workflow)
					results[noise][target_noise][workflow] = {}

					for cluster in clusters:
						# print("	  PLATFORMS: "+cluster)
						results[noise][target_noise][workflow][cluster] = {}

						cursor = collection.find({"file_size_factor":file_factor,"clusters": cluster, "workflow": workflow,"no_contention":False,"no_contention_in_speculative_executions":False,"no_amdahl_in_speculative_executions":True})
						us_makespans = []
						for doc in cursor:
							if (noise_reduction == 0.0) and (doc["disable_adaptation_if_noise_has_not_changed"] == False):
								continue
							is_us = (len(doc["task_selection_schemes"].split(",")) > 1) or (
									len(doc["cluster_selection_schemes"].split(",")) > 1) or (
											len(doc["core_selection_schemes"].split(",")) > 1)
							if not is_us:
								alg_name = doc["task_selection_schemes"] + "/" + doc["cluster_selection_schemes"] + "/" + \
										   doc["core_selection_schemes"]
								results[noise][target_noise][workflow][cluster][alg_name] = doc["makespan"]
							else:
								if (doc["simulation_noise"] == noise) and (
										doc["simulation_noise_reduction"] == noise_reduction):
									us_makespans.append(doc["makespan"])
						results[noise][target_noise][workflow][cluster]["us"] = us_makespans
		file_factor_dict[file_factor]=results
	write_results_to_file("yes_contention_no_amdahl_noise_extracted_results_"+version+".dict", file_factor_dict)

if __name__ == "__main__":
	main()
