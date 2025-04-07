## Simulating and Evolving Fish Schools in Settings with Predators and Food

This project was made for Natural Computing course at Radboud University by Ondřej Huvar, Tomáš Kalabis, Ariyan Tufchi.

This repository contains all code, results and instructions regarding the project.

## Project description

Essentially, we built a simulation that tries to imitate fish swarm behaviour in an environment with predators and food. The fish behaviour is modelled using Swarm Intelligence techniques, we use our custom extension of Boid algorithm. The resulting behaviour depends on a particular parameter setting.

You can then visualize the simulated fish behaviour using our web-based visualization tool.

Finally, we use evolutionary algorithms to slowly evolve various parameters that influence fish behaviour (cohesion, separation...). We study what types of behavioural strategies emerge, which parameters are most important for fish survival, and how evalutionary settings influence the results.

### Repository structure

Our codebase mainly consists of:
- higly optimized C++ simulation in the directory `simulation-cpp`
- JS-based visualization in the directory `visualization-js`
- parallelized Python implementation of the evolutionary algorithms in `evolution.py`

Our results are present in `results` directory.
Each set of experiments has its own subfolder with all the evolution logs, sometimes even overviews.
The directory also contains several GIF animations of various strategies in `animations` subfolder.

Below, we describe the individual components and how to run them in more detail.

## Installation and running

All of the code is developed and tested on WSL2 for Windows and on Linux.

### C++ simulation

All the simulation-related code is in the `simulation-cpp` directory, with the main logic in `main.cpp`.
To make installation and running easier, we provide:
- `Makefile` and `CMakeLists.txt` for the simulation binary compiling (see below)
- simulation binary pre-compiled for Linux (Ubuntu-20.0 WSL)
- an example log `output.json` of the simulation that can be used for the visualization directly

First, you will need C++ compiler, we use C++23.
Next, install dependencies for the cpp program:
```shell
sudo apt update
sudo apt install nlohmann-json3-dev
sudo apt install libboost-all-dev
```

The following command then builds and runs the simulation. The simulation prints the progress, and then outpts JSON log that can be used for visualization. 

```shell
make && ./cpp_simulation
```

You can also run the program with various arguments. Explore them like this:
```
./cpp_simulation --help
```

We have prepared `run_simulation.py` script in the main directory that executes the simulation with prepared parameters.

### JS Visualization

The main components of the visualization are `visualize.js`, `index.html`, and `style.css`. The visualization takes log from the simulation as its output, and displays the fish swarm behaviour in browser.

You can simply use VS Code and just start the `live server` at `index.html` to run the visualization of the last executed simulation.

### Python evolution

You will need Python interpreter, we use Python 3.10.11.

Simply run the evolution script as
```
python3 evolution.py 
```

The evolution may run for a longer time, depending on the selected parameters. To explore all different parameters of the evolution, use
```
python3 evolution.py --help
```
