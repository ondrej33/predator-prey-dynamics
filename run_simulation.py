import subprocess

# Define the command with the parameters derived during evolution
simulation_command = [
    "./simulation-cpp/cpp_simulation",
    "--debug", "true",
    "--fish-momentum", "0.7598",
    "--alignment", "0.426749",
    "--cohesion", "0.65982",
    "--separation", "0.76347",
    "--shark-repulsion", "8.51844",
    "--food-attraction", "2.88759"
]

# Execute the simulation
subprocess.run(simulation_command)

print("Simulation executed successfully, log for visualization saved to output.json.")
