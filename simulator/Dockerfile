FROM amd64/ubuntu:jammy

MAINTAINER Henri Casanova <henric@hawaii.edu>

# add repositories
RUN apt-get update

# set timezone
RUN echo "America/Los_Angeles" > /etc/timezone && export DEBIAN_FRONTEND=noninteractive && apt-get install -y tzdata

# build environment
RUN apt-get -y install pkg-config git cmake cmake-data libboost-all-dev wget sudo curl zip vim

# install compiler
RUN apt-get -y install gcc g++

#################################################
# WRENCH's dependencies
#################################################

# set root's environment variable
ENV CXX="g++" CC="gcc"
WORKDIR /tmp

# install SimGrid
RUN wget --no-check-certificate https://framagit.org/simgrid/simgrid/-/archive/v3.34/simgrid-v3.34.tar.gz && tar -xf simgrid-v3.34.tar.gz && cd simgrid-v3.34 && cmake . && make -j12 && sudo make install && cd .. && rm -rf simgrid-v3.34*


# install json for modern c++
RUN wget https://github.com/nlohmann/json/archive/refs/tags/v3.10.5.tar.gz && tar -xf v3.10.5.tar.gz && cd json-3.10.5 && cmake . && make -j4 && make install && cd .. && rm -rf v3.10.5* json-3.10.5

# install WRENCH
RUN git clone https://github.com/wrench-project/wrench.git  && cd wrench && git checkout 4c3b19b27b01352e492a434ec3b2db4e0f233bf6 && cmake . && make -j4 && sudo make install && cd .. && rm -rf wrench

# clone and install the scheduling_with_simulations_simulator with the right commit tab
RUN git clone https://github.com/wrench-project/scheduling_using_simulation_simulator.git && cd scheduling_using_simulation_simulator && git checkout ad1037a8a6d9e14e7e648d888a1f0440654b051d && mkdir build && cd build && cmake .. && make -j4 && sudo make install && cd ../.. && /bin/rm -rf scheduling_using_simulation_simulator/

# install pip
RUN wget https://bootstrap.pypa.io/get-pip.py && python3 get-pip.py && /bin/rm get-pip.py

# install pymongo
RUN python3 -m pip install pymongo

# install matplotlib
#RUN python3 -m pip install matplotlib

#################################################
# Non-root user 'me'
#################################################

RUN useradd -ms /bin/bash me 
RUN adduser me sudo
RUN echo '%sudo ALL=(ALL) NOPASSWD:ALL' >> /etc/sudoers

USER me
WORKDIR /home/me
RUN touch /home/me/.sudo_as_admin_successful

RUN git clone https://github.com/wrench-project/suss_experiments.git

ENV LD_LIBRARY_PATH=/usr/local/lib

