# Project for Natural Computing

- Simulating and evolving fish schools in environment with predators and food

- by Ondřej Huvar, Tomáš Kalabis, Ariyan Tufchi

# Project structure

This repository contains all code, results and instructions regarding the project.

Our code consists mainly of:
- simulation - `main.cpp`
- evolution - `evolution.py`
- visualization - `visualize.js`, `index.html`, `style.css`

To make running installation and running easier, we provide:
- `Makefile` and `CMakeLists.txt` for the simulation compiling (see next section)
- simulation binary pre-compiled for Linux (Ubuntu-20.0 WSL)
- log `output.json` of the simulation that can be used to run the visualization directly

Our results are present in `results` directory.
Each set of experiments has its own subfolder with all the evolution logs, sometimes even overviews.
The directory also contains some of the visualizations.

# Installation and running

All of the code is developed and tested on WSL2 for Windows and on Linux.

## C++ simulation
First, you will need C++ compiler, we use C++23.
Next, install dependencies for the cpp program:
```shell
sudo apt update
sudo apt install nlohmann-json3-dev
sudo apt install libboost-all-dev
```

Following command then builds and runs the simulation.
```shell
make && ./cpp_simulation
```

You can also run the program with various arguments. Explore them like this:
```
./cpp_simulation --help
```

## JS Visualization

You can simply use VS Code and just start the `live server` to run the visualization of the last simulation.

## Python evolution

You will need Python interpreter, we use Python 3.10.11.

Simply run the evolution as
```
python3 evolution.py 
```

To explore all different parameters of the evolution, use
```
python3 evolution.py --help
```
