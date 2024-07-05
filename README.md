# Supplemental Material and Reproducible Research for FGCS article

This repository contains **supplemental material** for the _An Exploration of Online-Simulation-driven Portfolio Scheduling in Workflow Management Systems_ article by McDonald et al. accepted for publication in the Future Generation Compute Systems journal. The supplemental material is available as a PDF in directory `supplemental_material`. 

This repository also contains **data, scripts, and code for making the
research in the above article reproducible**.  All result plots used in the
manuscript (and others that were omitted due to lack of space) are
available in the `./plot_analyze_results/plots_fgcs2024/` directory. The
content below details all the steps to generate these plots, which entails
running simulations, storing simulation output in a database, extracting
results from this database, and analyzing/plotting the results, all using
Python scripts included in this repository.

## Running all simulations

Complete experimental results are provided as a MongoDB dump in `./raw_data/dump.tgz`, and importing
these results into a locally running MongoDB can be done easily as: 
```
cd ./raw_data/
tar -xzf dump.zip
mongorestore
```
If you _really_ want to re-run everything, follow the steps below.  Otherwise, skip to the next section. 

### Step 1: Install the simulator code (in a Docker)

The simulator is hosted in [another
repository](https://github.com/wrench-project/scheduling_using_simulation_simulator).

A [Dockerfile](https://docs.docker.com/) image with the simulator installed in
`/usr/local/bin/scheduling_using_simulation_simulator` can be built from the [Dockerfile](https://docs.docker.com/engine/reference/builder/) in `./simulator/Dockerfile`.  This Dockerfile installs all required software with the appropriate versions and commit tags. 

To build the Docker image from this Docker file, invoke the following command in the top directory of this repository: 
```
docker build --no-cache -t fgcs2024 ./simulator/
```

### Step 2: Workflow JSON files

All JSON workflow description files, which are [WfCommons instances](https://wfcommons.org/instances), are available in the `./workflows/` directory.  Nothing to do here. 

### Step 3: Setup Mongo

The subsequent steps requires that a `mongod` daemon be started locally, so
that simulation output can be stored to and read from a MongoDB.   Here is 
a typical way to start a `mongod` that stores its data in directory `/tmp/db`

```
mkdir /tmp/db
mongod --dbpath /tmp/db 
```

### Step 4: Run all simulations

The scripts to run all simulations is available in `./run_script/network_versions`. This is a set of 3 scripts.  The `server.py` script takes as input a port to use and a MongoDB URL.  It then opens a server listening on that port.  From there `dispatch.py` can be used to dispatch experiments to the server, it takes a version, a server to dispatch to, a list of platform configurations to use, a list of workflow configurations to use, and then a sequence of arguments that describe the experiments to run.
Lastly `worker.py` can be ran on any number of parallel worker machines.  This script takes a server IP and the number of threads to use.
The workers must each have the platform configurations in the same relative path as the dispatcher does.

For instance, the command-lines below would run all experiments for producing all the data used in the manuscript using a 32 core worker, assuming the MongoDB daemon runs on the same host as the server.

###Server
Should be started inside a Docker container for the `fgcs2024` image.

```
cd ./run_scripts/network_versions
./server.py 8080 mongodb://localhost
```
###Worker
Should be started inside a Docker container for the `fgcs2024` image.

```
cd ./run_scripts/network_versions
./worker.py [serverURL]:8080 32
```

### Dispatcher

```
cd ./run_scripts/network_versions
./dispatcher.py v4 [serverURL]:8080 ../.. 0,1,2 0,1,2,3,4,5,6,7,8 --run-ideal
./dispatcher.py v4 [serverURL]:8080 ../.. 0,1,2 0,1,2,3,4,5,6,7,8 --run-noise 1000 1099

# Dispatch noise mitigation experiments
./dispatcher.py v4 [serverURL]:8080 ../.. 0,1,2 0,1,2,3,4,5,6,7,8 --run-noise 1000 1099 --run-mitigation

# Dispatch no contention experiments
./dispatcher.py v4 [serverURL]:8080 ../.. 0,1,2 0,1,2,3,4,5,6,7,8 --run-ideal --no-contention-in-speculative-executions
./dispatcher.py v4 [serverURL]:8080 ../.. 0,1,2 0,1,2,3,4,5,6,7,8 --run-noise 1000 1099 --no-contention-in-speculative-executions

# Dispatch no contention no Amdahl experiments
./dispatcher.py v5 [serverURL]:8080 ../.. 0,1,2 0,1,2,3,4,5,6,7,8 --run-ideal --no-amdahl-in-speculative-executions --no-contention-in-speculative-executions
./dispatcher.py v5 [serverURL]:8080 ../.. 0,1,2 0,1,2,3,4,5,6,7,8 --run-ideal --no-amdahl-in-speculative-executions 

# Dispatch no Amdahl experiments
./dispatcher.py v5 [serverURL]:8080 ../.. 0,1,2 0,1,2,3,4,5,6,7,8 --run-noise 1000 1099 --no-amdahl-in-speculative-executions --no-contention-in-speculative-executions
./dispatcher.py v5 [serverURL]:8080 ../.. 0,1,2 0,1,2,3,4,5,6,7,8 --run-noise 1000 1099 --no-amdahl-in-speculative-executions 
```
Alternatively, there is `dispatch-all.sh` which can be used to dispatch all of the experiments. 

```
dispatch-all.sh [serverURL]:8080
```

Several instances of the worker script can be started on multiple machines to parallelize the execution further, provided the server can be accessed remotely.

When not using the `--pre-validate` option, the dispatcher can be ran on a relatively slow computer without the simulator installed.

If using `--pre-validate`, then the dispatcher needs to run within a Docker container for image `fgcs2024`.


## Extracting and post-processing raw simulation output from MongoDB

A script to extract and post-process simulation output data from MongoDB 
is available in `./extract_script/extract_all_results.py`. This script takes as
argument a version string and a MongoDB URL. For instance, to extract all
results from a locally running MongoDB for all results in the manuscript, it should be invoked as:

```
cd ./extract_scripts
./extract_all_results.py fgcs2024 mongodb://localhost
```

The script generates several `*.dict` files in the `./extract_scripts` directory. These files are provided in this repository, so that you do not have to regenerate them. 

## Plotting/analyzing the simulation output

Scripts to plot/analyze extracted simulation output data are available in
the `./plot_analyze_results_scripts/` directory.  These scripts must be invoked from that directory, read in the `*.dict`
files in the `./extract_scripts/` directory, and generate `.pdf` plots and
text output, which are the basis for all presented simulation results and/or plots in the
paper. These scripts take in a version string. For instance, running the following command
in the `./plot_analyze_results_scripts` directory will produce **all** output:

```
cd ./plot_analyze_results_scripts
./plot_all_results.py fgcs2024
```

Text output is displayed in the terminal, and PDF files are generated in a
created `./plot_analyze_results_scripts/plots_fgcs2024` directory. These
files are included in this repository, so that you do not have to
regenerate them. Also included is file
`./plot_analyze_results_scripts/plot_all_results_script_output.txt`, which
contains the text output generated by the above script. Note that some of
the other scripts in that directory print out additional textual data,
which is included in the manuscript.

---
