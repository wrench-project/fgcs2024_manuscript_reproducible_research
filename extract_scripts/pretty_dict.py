#!/usr/bin/env python3
import sys
import ast


def pretty_dict(contents):
	contents=str(contents)
	output=""
	indent=0;
	indentC="    "
	escape='\0'
	newline=False
	for c in contents:
		
		if escape=='\0' and (c=='"' or c== '\''):
			escape=c
		elif escape==c:
			escape='\0'
		elif escape=='\0'and (c=='}'or c==']' or c==')'):
			output+='\n'
			indent-=1
			output+=indentC*indent
			newline=True
		if(newline):
			c=c.strip()
		if len(c)>0:
			newline=False
		output+=c
		if escape=='\0'and (c=='{' or c=='[' or c=='('):
			output+='\n'
			newline=True
			indent+=1
			output+=indentC*indent
		elif escape=='\0'and (c==','):
			output+='\n'
			newline=True
			output+=indentC*indent
	print(output)
	
if __name__ == "__main__":
	if (len(sys.argv) != 2):
		sys.stderr.write("Usage: " + sys.argv[0] + " <file to print>\n")
		sys.exit(0)
	try:
		input_file_name = sys.argv[1]
		file = open(input_file_name, "r")
	except OSError:
		sys.stderr.write("Could not open \""+input_file_name+"\"");
		sys.exit(1)
			
	contents = file.read()
	pretty_dict(contents)