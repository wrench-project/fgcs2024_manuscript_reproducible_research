#!/usr/bin/env python3
import socket
import sys
import time
import random
import subprocess
import glob
from multiprocessing import Pool
import json
import os
#from pymongo import MongoClient


# root_dir = os.path.abspath(sys.argv[2])

def run_simulation(arg, docker_prefix):
	command_to_run = arg

	# real_command_to_run = docker_prefix + "\"" + command_to_run + " 2> /dev/null\""
	# real_command_to_run =  command_to_run + " --print_JSON " + " 2> /dev/null"#this line is only for debugging
	real_command_to_run = command_to_run + " 2> /dev/null"  # this line is for inside the docker

	# Run the simulator
	print("Processing: " + real_command_to_run)
	json_output = subprocess.check_output(real_command_to_run, shell=True, stderr=subprocess.DEVNULL)
	results = json.loads(json_output)
	print("Processed")
	return results

def main(arg1):
	anti_nag=1;
	# docker_command = "docker run -d -v " + root_dir + ":/home/me jsspp_journal"
	# docker_container_id = subprocess.check_output(docker_command, shell=True).decode("utf-8").rstrip()
	# docker_prefix = "docker exec -it " + docker_container_id + " bash -c "
	server = arg1.split(":")
	while True:
		data = ""
		try:
			s = socket.socket()
			# s.settimeout(None)
			s.connect((server[0], int(server[1])))
			s.send(str({"cmd": "IDLE", "data": ""}).encode('utf-8'))
			data = s.recv(1024*1024).decode('utf-8')
			s.send("ACK".encode('utf-8'))
			s.close()
		except Exception as e:
			print(e)

		if (len(data) == 0 or data == "NONE"):
			time.sleep(30*anti_nag)
			anti_nag+=2
		else:
			anti_nag=2;
			# ret={"result":run_simulation(data,docker_prefix),"runcommand": data}
			ret = {"result": run_simulation(data, ""), "runcommand": data}
			pending = True
			while pending:
				try:
					s = socket.socket()
					s.connect((server[0], int(server[1])))
					s.send(str({"cmd": "RET", "data": ret}).encode('utf-8'))
					res = s.recv(1024).decode('utf-8')
					# print(res)
					if (res == "ACK"):
						pending = False
					s.close()
				except:
					time.sleep(60*anti_nag)
					anti_nag+=1
					


# docker_command = "docker kill " + docker_container_id
# os.system(docker_command)
# sys.stderr.write("\n")  # avoid weird terminal stuff?


if __name__ == "__main__":
	if len(sys.argv) < 3:
		sys.stderr.write("Usage: " + sys.argv[0] + " <server url> <num-threads>\n")
		sys.stderr.write("  For instance: " + sys.argv[0] + " [serverURL]:8080 `nproc`\n")
		sys.exit(1)
	num_threads = int(sys.argv[2])
	for i in range(num_threads - 1):
		time.sleep(1)
		pid = os.fork()
		if pid == 0:
			break
	main(sys.argv[1])
