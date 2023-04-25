import argparse
from datetime import datetime
from random import uniform, seed
import subprocess
from typing import TypeAlias
import time
from multiprocessing import Pool
from functools import partial


CHROMOSOME_LENGTH = 5
Individual: TypeAlias = list[float]


def generate_individual(individual_len: int) -> Individual:  
    """Randomly generate an individual of size `chromosome_len`."""
    return [uniform(0, 20) for _ in range(individual_len)]


def generate_population(
        num_population: int, 
        individual_len: int,
        ) -> list[Individual]:
    """Randomly generate whole population of size `num_individuals`."""
    return [generate_individual(individual_len) for _ in range(num_population)]


def get_simulation_result(individual: Individual) -> int:
    """Run the simulation with individual's parameters as arguments"""
    
    output = subprocess.run([
        './cpp_simulation', 
        '--debug', 'false',
        "--fish-momentum", str(individual[0]),
        "--alignment", str(individual[1]),
        "--cohesion", str(individual[2]),
        "--separation", str(individual[3]),
        "--shark-repulsion", str(individual[4]),
        ], stdout=subprocess.PIPE)
    output = output.stdout.decode("utf-8").strip()

    # output is in form "TOTAL FISH EATEN: N" - return the number
    return int(output.split()[-1])


def eval_individual(
        individual: Individual, 
        simulations_per_indiv: int
        ) -> float:
    """
    Evaluate fitness of a `individual`.
    That means run the simulation `simulations_per_indiv` times, and take average.
    We will run them in parallel.
    """
    # run all simulations in parallel
    with Pool(simulations_per_indiv) as pool:
        async_results = [pool.apply_async(get_simulation_result, args=([individual])) for _ in range(simulations_per_indiv)]
        results = [ar.get() for ar in async_results]
        return sum(results) / simulations_per_indiv
    

def eval_population(
        population: list[Individual], 
        simulations_per_indiv: int
        ) -> list[tuple[Individual, float]]:
    """Evaluate fitness of whole population, return list of tuples <individual, fitness>."""
    return [(indiv, eval_individual(indiv, simulations_per_indiv)) for indiv in population]


def get_fittest_individual(
        population_with_fitness: list[tuple[Individual, float]]
        ) -> tuple[Individual, float]:
    """
    Return the fittest individual from the population (tuples <indiv, fitness>).
    That means the individual with least killed fish.
    """
    return min(population_with_fitness, key=lambda x: x[1])


def selection_step():
    """Select parents for reproduction."""
    # TODO
    pass


def crossover():
    """Do a crossover of the 2 parents, return both children."""
    # TODO
    pass


def mutate():
    """Mutate the given `individual`."""
    # TODO
    pass


def reproduction_step():
    """Generate new offspring set from parents by applying crossover and mutations."""
    # TODO: if needed shuffle the parents first, so that the order is 'random'

    # TODO: do crossovers

    # TODO: apply mutations

    pass


def replacement_step():
    """
    Replace the old population with the new one. Take parents+offsprings, and 
    using some strategy, select new population.
    """
    # TODO
    pass


def evolution(
    mutation_prob,
    population_size,
    generations_max,
    simulations_per_indiv,
    len_individual,
    debug=False,
):
    """Run the whole evolution process."""
    start = time.time()

    # generate the population and evaluate it
    population = generate_population(population_size, len_individual)
    population_with_fitness = eval_population(population, simulations_per_indiv)
    # get the best individual of the new population and log it
    print(f"GEN 0, TIME {time.time() - start},", get_fittest_individual(population_with_fitness), flush=True)

    iteration = 0
    while iteration < generations_max:
        iteration += 1

        # TODO: select parents from the population
        selection_step()

        # TODO: generate new offspring set (do the crossovers and mutations)
        reproduction_step()

        # TODO: replace generations and evaluate the new individuals
        replacement_step()
 
        # TODO: evaluate new population (now just placeholder)
        # TODO: only eval individuals from the new population
        population_with_fitness = eval_population(population, simulations_per_indiv)

        # TODO: get the best individual of the new population and log it
        print(f"GEN {iteration}, TIME {time.time() - start},", get_fittest_individual(population_with_fitness), flush=True)

    # TODO: summarize and return fittest?
    end = time.time()
    print(f"Total time:", end - start)



def main(
        mutation_prob, 
        population_size, 
        generations_max, 
        simulations_per_indiv, 
        len_individual,
        debug=False,
        ):
    # TODO: prepare some things
    
    # TODO: run evolution
    evolution(
        mutation_prob, 
        population_size, 
        generations_max, 
        simulations_per_indiv,
        len_individual,
        debug,
    )
    
    # TODO: sum up the results
    pass


if __name__ == "__main__":
    # parse CLI arguments

    parser = argparse.ArgumentParser(
        prog='Natural computing, project',
        description='Runs algorithm for evolution of fish swarms',
    )

    # algorithm parameters (all tunable, but with default values)
    parser.add_argument('-m', '--mutation_prob', default=0.02)
    parser.add_argument('-p', '--population_size', default=10) # ideally use 100+
    parser.add_argument('-g', '--generations_max', default=10) # ideally use 200+
    parser.add_argument('-s', '--simulations_per_indiv', default=8) # ideally use 10
    parser.add_argument('-l', '--len_individual', default=5)
    parser.add_argument('-r', '--random_seed', default=True)
    parser.add_argument('-d', '--debug', default=True)
    args = parser.parse_args()

    if args.random_seed:
        seed(datetime.now().timestamp())
    else:
        seed(42)

    main(
        args.mutation_prob, 
        args.population_size, 
        args.generations_max, 
        args.simulations_per_indiv,
        args.len_individual,
        args.debug,
    )