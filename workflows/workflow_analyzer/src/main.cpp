/**
 * Copyright (c) 2020. <ADD YOUR HEADER INFORMATION>.
 * Generated with the wrench-init.in tool.
 *
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 */
#include <wrench.h>
#include <memory>
#include <boost/program_options.hpp>
#include <random>
#include <nlohmann/json.hpp>
#include <sstream>


namespace po = boost::program_options;

int main(int argc, char **argv) {

    // Declaration of the top-level WRENCH simulation object
    auto simulation = wrench::Simulation::createSimulation();

    // Initialization of the simulation
    simulation->init(&argc, argv);

    // Define command-line argument options
    std::string workflow_file;

    po::options_description desc("Allowed options");
    desc.add_options()
            ("help",
             "Show this help message\n")
            ("workflow", po::value<std::string>(&workflow_file)->required()->value_name("<path>"),
             "Path to JSON workflow description file\n")
            ;

    // Parse command-line arguments
    po::variables_map vm;
    po::store(
            po::parse_command_line(argc, argv, desc),
            vm
    );

    try {
        // Print help message and exit if needed
        if (vm.count("help")) {
            std::cerr << desc << "\n";
            exit(0);
        }
        // Throw whatever exception in case argument values are erroneous
        po::notify(vm);
    } catch (std::exception &e) {
        cerr << "Error: " << e.what() << "\n";
        exit(1);
    }

    // Parse the workflow
    // As a performance optimization, in this whole simulator, instead of calling getMinNumCores() and getMaxNumCores(), we just
    // hardcode 1 and 64. Check out the macros.
    std::string reference_flops = "1f";
    auto workflow = wrench::WfCommonsWorkflowParser::createWorkflowFromJSON(
            workflow_file, reference_flops, true, false, true, 1, 1, true, true, false);

    std::cout << "#Files: " << workflow->getFileMap().size() << " ";
    std::cout << "#Tasks: " << workflow->getTasks().size() << " ";
    double work = 1;
    for (auto const &task : workflow->getTasks()) {
        work += task->getFlops();
    }
    std::cout << "Work: " << (((int)work) / 3600) << "h" << (((int)work % 3600) / 60) << "m ";
    double footprint = 0;
    for (auto const &file : workflow->getFileMap()) {
       footprint += (int)file.second->getSize();
    }

    std::stringstream stream;
    std::string footprint_string;
    if (footprint < 1000) {
        stream << std::fixed << std::setprecision(2) << footprint;
        footprint_string = stream.str() +  "B";
    } else if (footprint < 1000000) {
        stream << std::fixed << std::setprecision(2) << footprint/1000;
        footprint_string = stream.str() +  "KB";
    } else if (footprint < 1000000000) {
        stream << std::fixed << std::setprecision(2) << footprint/1000000;
        footprint_string = stream.str() +  "MB";
    } else {
        stream << std::fixed << std::setprecision(2) << footprint/1000000000;
        footprint_string = stream.str() +  "GB";
    }
    std::cout << "Footprint: " << footprint_string << " ";

    std::cout << "Depth: " << workflow->getNumLevels() << " ";
    unsigned long max_width = 0;
    for (int i=0; i < workflow->getNumLevels()-1; i++) {
        max_width = std::max<unsigned long>(max_width, workflow->getTasksInTopLevelRange(i, i+1).size());
    }
    std::cout << "MaxWidth: " << max_width << "\n";

    return 0;
}

