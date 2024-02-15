#!/usr/bin/env python3
import glob
import sys
import subprocess


workflow_names = {}
workflow_names["1000genome"] = [r"$W_{\genome}$","1000Genomes"]
workflow_names["blast"] = [r"$W_{\blast}$","BLAST"]
workflow_names["bwa"] = [r"$W_{\bwa}$","BWA"]
workflow_names["cycles"] = [r"W_{\cycles}$","Cycles"]
workflow_names["epigenomics"] = [r"$W_{\epigenomics}$","Epigenomics"]
workflow_names["rnaseq"] = [r"$W_{\rnaseq}$","RNA-Seq"]
workflow_names["soykb"] = [r"$W_{\soykb}$","SoyKB"]
workflow_names["srasearch"] = [r"$W_{\srasearch}$","SRA-Search"]
workflow_names["viralrecon"] = [r"$W_{\viralrecon}$","Viralrecon"]

order = ["1000genome", "blast", "bwa", "cycles", "epigenomics", "rnaseq", "soykb", "srasearch", "viralrecon"]



results = {}
json_files = glob.glob('./*.json', recursive = True)
for json_file in json_files:
    workflow_name = json_file.split("/")[1].split("-")[0]
    output = subprocess.getoutput(f"./workflow_analyzer/build/workflow_analyzer --workflow {json_file}")
    tokens = output.split(" ")
    results[workflow_name] = [tokens[1], tokens[3], tokens[5], tokens[7], tokens[9], tokens[11]]

print("--------------------------")
print(r"""\begin{tabular}{clrrrrrrr}
    \toprule
        Workflow & Name & \#Tasks & Work & \#Files & Footprint & Depth & Max Width\\
    \midrule""")
flip = 0
for workflow_name in order:
    if flip == 1:
        print(r"""    \rowcolor{Gray}""")
    [num_files, num_tasks, work, footprint, depth, maxwidth] = results[workflow_name]
    print(f"""        {workflow_names[workflow_name][0]} & {workflow_names[workflow_name][1]} & {num_tasks} & {work} & {num_files} & {footprint} & {depth} & {maxwidth}\\\\""")
    flip = 1 - flip

print(r"""    \bottomrule
\end{tabular}""")



