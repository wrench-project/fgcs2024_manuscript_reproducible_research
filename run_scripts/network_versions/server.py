#!/usr/bin/env python3
import socket
import sys
import time
import ast
import random
import subprocess
import glob
import threading
from multiprocessing import Pool
import json
import os
from pymongo import MongoClient
todoLock=threading.Lock()
todo = []
import traceback
from datetime import datetime, date

def nextAST(s):
	data = ""
	try:
		while True:
			newData = s.recv(1024 * 1024).decode('utf-8')
			if not newData:
				break
			data += newData
			try:
				# print(data)
				ret = ast.literal_eval(data)
				return ret
			except:
				pass
	except Exception as e: 
		print(e)
		return None


def readyNext(mydb, remove=True):
	ret = None
	#print("LOCK 38 db acquire")		
	with dbLock:
	#print("LOCK 40 todo acquire")
		with todoLock:
			while True:
				if (len(todo) == 0):
					break
				next = todo[0]
				cmd = next[0]
				db = next[1]
				print_json_command_to_run = cmd + " --print_JSON " + " 2> /dev/null"
				try:
					# print(print_json_command_to_run)
					json_output = subprocess.check_output(print_json_command_to_run, shell=True)
					config = json.loads(json_output)
					collection = mydb["results_" + db]

					if collection.find_one(config):
						todo.remove(todo[0])
				
					# sys.stderr.write(".")
					# sys.stderr.flush()
					else:
						ret = next
						if(remove):
							todo.remove(next)
						break
				except:
					print('Error when processing command "'+print_json_command_to_run+'"\n', file=sys.stderr)
					
					traceback.print_exc()
	return ret
	
ingestLock=threading.Lock()
def connectionThread(c,addr,mydb):
	global todo
	print("[",date.today(), datetime.now().strftime("%H:%M:%S"),']', end=' ')
	try:
			print('Got connection from', addr)
			rec = nextAST(c)
			if not rec:
				print("	Invalid message")
				c.close()
				return
			# print(rec)
			# print(rec)
			# rec=ast.literal_eval(rec.decode('utf-8'))
			command = rec["cmd"]

			if (command == "IDLE"):
				if ingestLock.locked():
					print("	Contacted durring ingest, ignoring")
					c.send("NONE".encode('utf-8'))
					ack = c.recv(1024)
				else:
					print("	" + str(addr) + " Requested Task")
					next = readyNext(mydb)
					#print("LOCK 83 todo acquire")
					
						
					if next:
						print("	Sending task")
						c.send(str(next[0]).encode('utf-8'))
						ack = c.recv(1024)
						print(ack)
						if (ack == "ACK".encode('utf-8')):
							print("	Acknowledged")
							#print("LOCK 94 ds acquire")
							with dispatchedLock:
							
								dispatched[next[0]] = {"time": time.time(), "request": next, "db": next[1]}
								#print("LOCK 98 ds release")
								
							
						else:
							print("	Not Acknowledged")
							with todoLock:
								todo.append(next)
					else:
						print("	Nothing to do")
						c.send("NONE".encode('utf-8'))
						ack = c.recv(1024)
						#print("LOCK 108 todo release")
					readyNext(mydb,False)
			elif (command == "RET"):
				print("	Receiving result")
				data = rec["data"]
				c.send("ACK".encode('utf-8'))
				# add result to database
				#print("LOCK 115 db acquire")
				with dbLock:
					try:
						#print("LOCK 123 ds acquire")
						with dispatchedLock:
							collection = mydb["results_" + dispatched[data["runcommand"]]["db"]]
							result = data["result"]
							collection.insert_one(result)
						# print(data)
							
							
							dispatched.pop(data["runcommand"])
					except KeyError:
						pass
						
					#print("LOCK 133 db release")	
				
				
			elif (command == "ADD"):
				data = rec["data"]
				print(str(addr) + " Adding tasks")			
				#print("LOCK 139 todo aquire")
				
				#print("LOCK Locking Injest lock")
				with ingestLock:
					print("  potential deadlock ",end='')
					sys.stdout.flush()
					with todoLock:
						print("cleared")
						
						for d in sorted(data,key=lambda _: random.random()):
							# print("adding "+str(d))
							todo.append(d)
						#print("LOCK 145 todo release")
					print("	Added " + str(len(data)) + " tasks")
					c.send("ACK".encode('utf-8'))
					print("	ingesting...")
					readyNext(mydb,False)
					#print("LOCK Releasing ingest lock")
				
				print("	ready")
			elif (command=="CLEAR"):
				print("	clearing cache")
				cleanCache(time.time())
			elif (command=="PURGE"):
				print("	purging todo")
				with todoLock:
					todo=[]
			elif (command=="COUNT"):
				with todoLock:
					print("TODO "+str(len(todo)))
					c.send(("TODO "+str(len(todo))).encode('utf-8'))
			else:
				print("	unknown command: " + str(rec["cmd"]) + str(rec))
	finally:			
			c.close()
dispatchedLock=threading.Lock()
dispatched = {}
dbLock=threading.Lock()
def cleanCache(lastCleanup):
#print("LOCK 185 todo acquire")
	with todoLock:
		#print("LOCK 187 ds acquire")
		print("  potential deadlock ",end='')
		with dispatchedLock:
		
			print("cleared")
			
			for key in dispatched:
				if (dispatched[key]["time"] < lastCleanup):
					data=dispatched[key]["request"]
					todo.append(data)
					dispatched.pop(data)
			#print("LOCK 192 ds release")
		#print("LOCK 194 todo release")
	
	lastCleanup = time.time()
	print(  "  cache cleaned at "+str(lastCleanup))
def main(port, database):
	lastCleanup = time.time()
	# server=arg1.split(":")
	s = socket.socket()
	s.settimeout(1)
	s.bind(("", int(port)))
	s.listen(4096)

	mongo_client = MongoClient(host=database, serverSelectionTimeoutMS=1000)
	mydb = mongo_client["scheduling_with_simulation"]
	while True:
		try:

			# print("Waiting for collection")
			c, addr = s.accept()
			try:
				threading.Thread(target=connectionThread, args=(c,addr,mydb)).start()
			except:
				try:
					c.close();
				except:
					pass
		except socket.timeout:
			pass
		
		# except Exception as e:
		# print("Error with client ")
		# print(e)
		
		if lastCleanup - time.time() > 86400:
			cleanCache(lastCleanup)
	mongo_client.close()


if __name__ == "__main__":
	try:
		if len(sys.argv) != 3:
			sys.stderr.write("Usage: " + sys.argv[0] + " <port> <mongo url>\n")
			sys.stderr.write("  For instance: " + sys.argv[0] + " 8080 mongodb://localhost\n")
			sys.exit(1)
		print("Activating server on "+sys.argv[1]+" "+sys.argv[2]+" with PID "+str(os.getpid()))
		main(sys.argv[1], sys.argv[2])
	except KeyboardInterrupt:
		pass
	except OSError as e:
		print(e)
	except NameError as e:
		print(e)
