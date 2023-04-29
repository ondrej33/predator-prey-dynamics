import argparse
from datetime import datetime
import random
import subprocess
from typing import TypeAlias
import time
from multiprocessing import Pool
from functools import partial


CHROMOSOME_LENGTH = 5
Individual: TypeAlias = list[float]


def generate_individual(individual_len: int) -> Individual:  
    """Randomly generate an individual of size `chromosome_len`."""
    return [random.uniform(0, 20) for _ in range(individual_len)]


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


def get_n_fittest_individuals(
        population_with_fitness: list[tuple[Individual, float]],
        n: int,
        ) -> tuple[Individual, float]:
    """Return the N fittest individual from the population (tuples <indiv, fitness>)."""
    return sorted(population_with_fitness, key=lambda x: x[1])[:n]


def tournament_step(population_with_fitness, k) -> Individual:
    """Randomly select `k` individuals and take the best one."""
    selected_k = random.choices(population_with_fitness, k=k)
    return get_fittest_individual(selected_k)[0]


def tournament_selection(population_with_fitness, k) -> list[Individual]:
    """
    Select parents for reproduction using tournament (of size `k`) selection.
    For now, we select `population_size` parents, with repetition.
    """
    selected_parents = []
    population_size = len(population_with_fitness)
    for _ in range(population_size):
        selected_parents.append(tournament_step(population_with_fitness, k))
    return selected_parents


def selection_step(population_with_fitness, tournament_k) -> list[Individual]:
    """Select parents for reproduction. For now, we use tournament."""
    return tournament_selection(population_with_fitness, tournament_k)


def crossover(parent1: Individual, parent2: Individual) -> tuple[Individual, Individual]:
    """Do a crossover of the 2 parents, return both children."""
    offspring1: Individual = []
    offspring2: Individual = []

    # for now, randomly take each gene from one of the parents
    for i in range(len(parent1)):
        parent_choice = random.choice([True, False])
        if parent_choice:
            offspring1.append(parent1[i])
            offspring2.append(parent2[i])
        else:
            offspring1.append(parent2[i])
            offspring2.append(parent1[i])

    return (offspring1, offspring2)


def mutate(individual: Individual, mutation_prob: float) -> Individual:
    """
    Mutate the given `individual`.
    Mutation probability is a probablity of mutating each gene of the individual.
    """
    mutated = individual.copy()
    for i in range(len(mutated)):
        # decide if to mutate or not
        if random.random() < mutation_prob:
            # decide if to make larger or smaller and select the multiplication factor
            # TODO: make better
            factor = random.uniform(0.5, 1)
            if random.random() < 0.5:
                mutated[i] *= factor
            else: 
                mutated[i] /= factor
    return mutated


def reproduction_step(
        selected_parents: list[Individual], 
        mutation_prob: float,
        crossover_prob: float,
        ) -> list[Individual]:
    """
    Generate new offspring set from parents by applying crossover and mutations.
    Mutation probability is probablity of mutating each gene of the individual.
    Crossover probability is probablity of combining selected pairs of parents.
    """
    # shuffle the selected parents first, so that the order is 'random'
    random.shuffle(selected_parents)

    offspring_population = selected_parents.copy()

    # do crossovers and add results to offspring population
    for i in range(1, len(selected_parents), 2):
        if random.random() < crossover_prob:
            offspring_population.extend(crossover(selected_parents[i - 1], selected_parents[i]))

    # apply mutations to all offsprings
    offspring_population = map(lambda x: mutate(x, mutation_prob), offspring_population)

    return list(offspring_population)


def elitist_replacement(
        population_with_fitness: list[tuple[Individual, float]], 
        offsprings_with_fitness: list[tuple[Individual, float]],
        ) -> list[tuple[Individual, float]]:
    """Use elitism to get new population from the previous population + offsprings."""
    population_size = len(population_with_fitness)

    combined_population = population_with_fitness.copy()
    combined_population.extend(offsprings_with_fitness)
    combined_population.sort(key=lambda x: x[1])
    return combined_population[:population_size]


def replacement_step(
        population_with_fitness: list[tuple[Individual, float]], 
        offsprings_with_fitness: list[tuple[Individual, float]],
        ) -> list[tuple[Individual, float]]:
    """
    Combine the previous population and new offsprings to get new population. 
    Takes both parents+offsprings, and using some strategy, select new population.
    For now we take elitist approach.
    """
    return elitist_replacement(population_with_fitness, offsprings_with_fitness)


def evolution(
    mutation_prob: float,
    crossover_prob: float,
    population_size: int,
    generations_max: int,
    simulations_per_indiv: int,
    len_individual: int,
    start_time: float,
    n_best_to_return: int,
    debug: bool = False,
) ->  list[tuple[Individual, float]]:
    """Run the whole evolution process."""
    TOURNAMENT_K = 5 # for now, we'll use tournament selection, will change

    # generate the population and evaluate it
    population = generate_population(population_size, len_individual)
    population_with_fitness = eval_population(population, simulations_per_indiv)
    # get the best individual of the new population and log it
    print(f"GEN 0, TIME {time.time() - start_time},", get_fittest_individual(population_with_fitness), flush=True)

    iteration = 0
    while iteration < generations_max:
        iteration += 1

        # select parents from the population
        selected_parents = selection_step(population_with_fitness, TOURNAMENT_K)

        # generate new offspring set (do the crossovers and mutations)
        generated_offsprings = reproduction_step(selected_parents, mutation_prob, crossover_prob)

        # evaluate fitness of the offspring population
        offsprings_with_fitness = eval_population(generated_offsprings, simulations_per_indiv)

        # create new population using the old and new populations
        population_with_fitness = replacement_step(population_with_fitness, offsprings_with_fitness)
 
        # get the best individual of the new population and log it
        print(f"GEN {iteration}, TIME {time.time() - start_time},", get_fittest_individual(population_with_fitness), flush=True)

    # return the fittest individual
    return get_n_fittest_individuals(population_with_fitness, n_best_to_return)



def main(
        mutation_prob: float, 
        crossover_prob: float,
        population_size: int, 
        generations_max: int, 
        simulations_per_indiv: int, 
        len_individual: int,
        n_best_to_return: int,
        debug: bool = False,
        ):
    # prepare some things and logging
    start = time.time()
    if debug:
        print("Starting computation.\n")
    
    # run the evolution
    n_best_individuals = evolution(
        mutation_prob, 
        crossover_prob,
        population_size, 
        generations_max, 
        simulations_per_indiv,
        len_individual,
        start,
        n_best_to_return,
        debug,
    )
    
    # sum up the results
    end = time.time()
    if debug:
        print("Computation finished.")
        print(f"{n_best_to_return} best individuals of the last generation:")
        for indiv in n_best_individuals:
            print(f">>    {indiv}")
        print(f"Total time:", end - start)


if __name__ == "__main__":
    # parse CLI arguments

    parser = argparse.ArgumentParser(
        prog='Natural computing, project',
        description='Runs algorithm for evolution of fish swarms',
    )

    # algorithm parameters (all tunable, but with default values)
    parser.add_argument('-m', '--mutation_prob', default=0.2)
    parser.add_argument('-c', '--crossover_prob', default=0.2)
    parser.add_argument('-p', '--population_size', default=10) # ideally use 100+
    parser.add_argument('-g', '--generations_max', default=20) # ideally use 200+
    parser.add_argument('-s', '--simulations_per_indiv', default=8) # ideally use 8-16, depend on cores
    parser.add_argument('-l', '--len_individual', default=5)
    parser.add_argument('-r', '--random_seed', default=True)
    parser.add_argument('-n', '--n_best_to_return', default=10)
    parser.add_argument('-d', '--debug', default=True)
    args = parser.parse_args()

    if args.random_seed:
        random.seed(datetime.now().timestamp())
    else:
        random.seed(42)

    if args.debug:
        print("Parameters:")
        print(args)
        print()

    main(
        args.mutation_prob, 
        args.crossover_prob, 
        args.population_size, 
        args.generations_max, 
        args.simulations_per_indiv,
        args.len_individual,
        args.n_best_to_return,
        args.debug,
    )