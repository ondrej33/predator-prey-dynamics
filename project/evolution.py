import argparse
from datetime import datetime
import random
import subprocess
from typing import TypeAlias
import time
from multiprocessing import Pool
from functools import partial
from copy import deepcopy


Individual: TypeAlias = list[float]


def log(file, content, also_print=True, end="\n"):
    file.write(content + end)
    file.flush()
    if also_print:
        print(content, end=end)


def generate_individual(individual_len: int) -> Individual:  
    """
    Randomly generate an individual of size `chromosome_len`.
    Sample from from 2 different distributions - [0,1] and [1,10] - to achieve diverse (both small & larger) values.
    """
    # select which distribution (low or high) will be used to get value for each parameter
    distrib_choices = [random.random() > 0.5 for _ in range(individual_len)]
    # randomly sample from low or high distributions
    return [random.uniform(1, 10) if choice else random.random() for choice in distrib_choices]


def generate_population(
        num_population: int, 
        individual_len: int,
        ) -> list[Individual]:
    """Randomly generate whole population of size `num_individuals`."""
    return [generate_individual(individual_len) for _ in range(num_population)]


def get_simulation_result(individual: Individual) -> tuple[int, int]:
    """Run the simulation with individual's parameters as arguments"""
    
    output = subprocess.run([
        './cpp_simulation', 
        '--debug', 'false',
        "--fish-momentum", str(individual[0]),
        "--alignment", str(individual[1]),
        "--cohesion", str(individual[2]),
        "--separation", str(individual[3]),
        "--shark-repulsion", str(individual[4]),
        "--food-attraction",  str(individual[5]),
        ], stdout=subprocess.PIPE)
    output = output.stdout.decode("utf-8").strip()

    # output is in form "TOTAL FISH EATEN: N\nTOTAL FOOD EATEN: N" - return the number
    return int(output.split('\n')[0].split()[-1]), int(output.split('\n')[1].split()[-1])


def eval_individual(
        individual: Individual, 
        simulations_per_indiv: int,
        food_weight: float
        ) -> float:
    """
    Evaluate fitness of a `individual`.
    That means run the simulation `simulations_per_indiv` times, and take average.
    We will run them in parallel.
    """
    # run all simulations in parallel
    with Pool(simulations_per_indiv) as pool:
        async_results = [pool.apply_async(get_simulation_result, args=([individual])) for _ in range(simulations_per_indiv)]
        result_tuples = [ar.get() for ar in async_results]
        # results are pairs of <fish_dead, food_eaten>, combine them to get one number
        aggregated_results = [res_tuple[0] - food_weight * res_tuple[1] for res_tuple in result_tuples]
        return sum(aggregated_results) / simulations_per_indiv
    

def eval_population(
        population: list[Individual], 
        simulations_per_indiv: int,
        food_weight: float
        ) -> list[tuple[Individual, float]]:
    """Evaluate fitness of whole population, return list of tuples <individual, fitness>."""
    return [(indiv, eval_individual(indiv, simulations_per_indiv, food_weight)) for indiv in population]


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


def tournament_selection(population_with_fitness, k, num_parents=None) -> list[Individual]:
    """
    Select parents for reproduction using tournament (of size `k`) selection.
    For now, we select `population_size` parents, with repetition.
    """
    selected_parents = []
    if num_parents == None:
        num_parents = len(population_with_fitness)
    for _ in range(num_parents):
        selected_parents.append(tournament_step(population_with_fitness, k))
    return selected_parents


def universal_sampling(
        population_with_fitness: list[tuple[Individual, float]],
        num_parents: int
        ) -> list[Individual]:
    """
    Perform stochastic universal sampling to select parents for reproduction.
    Selects `num_parents` parents from the population.
    """
    # Descending Sort
    population_with_fitness.sort(key=lambda x: x[1], reverse=True)
    # cal total fitness
    total_fitness = sum(fitness for _, fitness in population_with_fitness)
    # for analysis or some shit
    # fitness_percentages = [fitness / total_fitness for _, fitness in population_with_fitness]
    # step size for the roulette
    step_size = total_fitness / num_parents
    # Random starting point
    start_pos = random.uniform(0, step_size)
    parents = []
    current_pos = start_pos
    # sum of fitness for the loop
    added_fitness = 0

    for individual, fitness in population_with_fitness:
        added_fitness += fitness
        while added_fitness >= current_pos:
            parents.append(individual)
            current_pos += step_size

    return parents


def selection_step(
        population_with_fitness, 
        tournament_k, 
        num_parents=None
        ) -> list[Individual]:
    """Select parents for reproduction. For now, we use tournament."""
    
    #return universal_sampling(population_with_fitness, num_parents)
    
    return tournament_selection(population_with_fitness, tournament_k, num_parents)


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
    mutated = deepcopy(individual)
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
        mutation_copies: int,
        ) -> list[Individual]:
    """
    Generate new offspring set from parents by applying crossover and mutations.
    Mutation probability is probablity of mutating each gene of the individual.
    Crossover probability is probablity of combining selected pairs of parents.
    Mutation copies is how many copies of each of the indivs (both selected parents and new offsprings) are used before applying mutations.
    """
    # shuffle the selected parents first, so that the order is 'random'
    random.shuffle(selected_parents)

    # first copy the parents (this copy will be only used for mutations later)
    offspring_population = deepcopy(selected_parents)

    # do crossovers and add results to offspring population
    for i in range(1, len(selected_parents), 2):
        if random.random() < crossover_prob:
            offspring_population.extend(crossover(selected_parents[i - 1], selected_parents[i]))

    # generate `mutation_copies` copies of each indiv in current "offspring" population
    offspring_population_copy = deepcopy(offspring_population)
    for i in range(mutation_copies - 1):
        offspring_population.extend(offspring_population_copy)
    # apply mutations to all of these individuals one by one
    offspring_population = map(lambda x: mutate(x, mutation_prob), offspring_population)

    return list(offspring_population)


def are_too_similar(indiv1: Individual, indiv2: Individual)-> bool:
    """Check if two individuals are so similar that they can be considered redundant."""
    for i in range(len(indiv1)):
        if indiv1[i] - indiv2[i] > 1e-2:
            return False
        # if the value is too small, consider smaller treshold
        if min(indiv1[i], indiv2[i]) < 1e-2 and indiv1[i] - indiv2[i] > 1e-4:  
            return False
        
    return True


def remove_duplicates(
        combined_population: list[tuple[Individual, float]]
        )-> list[tuple[Individual, float]]:
    """Remove redundant copies of the same individuals to not lose diversity."""
    unique_population = []

    for (indiv, score1) in combined_population:
        skip_indiv = False
        # TODO: choose how to choose new score for the duplicates
        for (unique_indiv, score2) in unique_population:
            if are_too_similar(indiv, unique_indiv):
                skip_indiv = True
                break
        if not skip_indiv:
            unique_population.append((indiv, score1))
    return unique_population
            

def elitist_replacement(
        population_with_fitness: list[tuple[Individual, float]], 
        offsprings_with_fitness: list[tuple[Individual, float]],
        ) -> list[tuple[Individual, float]]:
    """Use elitism to get new population from the previous population + offsprings."""
    population_size = len(population_with_fitness)

    combined_population = deepcopy(population_with_fitness)
    combined_population.extend(offsprings_with_fitness)
    # sort the population based on fitness
    combined_population.sort(key=lambda x: x[1])
    # Remove redundant copies of the same individuals to not lose diversity
    combined_population = remove_duplicates(combined_population)
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


def log_generation_info(
        generation: int,
        run_time: float, 
        population_with_fitness: list[tuple[Individual, float]],
        log_file,
        ):
    log(log_file, f"GEN {generation}, TIME {run_time:.2f}, PARAMS: [ ", end="")
    fittest_indiv, score = get_fittest_individual(population_with_fitness)
    for param in fittest_indiv:
        log(log_file, f"{param:.5f}", end=", ")
    log(log_file, f"], SCORE: {score:.2f}")


def log_individual_with_fitness(indiv_w_fitness: tuple[Individual, float], log_file):
    log(log_file, "[", end="")
    for value in indiv_w_fitness[0]:
        log(log_file, f"{value:.5f}", end=", ")
    log(log_file, "]", end="  ")
    log(log_file, f"{indiv_w_fitness[1]:.5f}")


def evolution(
    mutation_prob: float,
    crossover_prob: float,
    population_size: int,
    generations_max: int,
    simulations_per_indiv: int,
    len_individual: int,
    mutation_copies: int,
    start_time: float,
    n_best_to_return: int,
    food_weight: float,
    log_file,
    debug: bool = False,
) ->  list[tuple[Individual, float]]:
    """Run the whole evolution process."""
    TOURNAMENT_K = 7 # for now, we'll use tournament selection, this may change?

    # generate the population and evaluate it
    population = generate_population(population_size, len_individual)
    population_with_fitness = eval_population(population, simulations_per_indiv, food_weight)
    # get the best individual of the new population and log it
    log_generation_info(0, time.time() - start_time, population_with_fitness, log_file)

    iteration = 0
    while iteration < generations_max:
        iteration += 1

        # select parents from the population
        selected_parents = selection_step(population_with_fitness, TOURNAMENT_K)

        # generate new offspring set (do the crossovers and mutations)
        generated_offsprings = reproduction_step(selected_parents, mutation_prob, crossover_prob, mutation_copies)

        # evaluate fitness of the offspring population
        offsprings_with_fitness = eval_population(generated_offsprings, simulations_per_indiv, food_weight)

        if debug:
            for i in sorted(population_with_fitness, key=lambda x: x[1]):
                log(log_file, "p ", end="")
                log_individual_with_fitness(i, log_file)
            for i in sorted(offsprings_with_fitness, key=lambda x: x[1]):
                log(log_file, "o ", end="")
                log_individual_with_fitness(i, log_file)
            log(log_file, "")

        # create new population using the old and new populations
        population_with_fitness = replacement_step(population_with_fitness, offsprings_with_fitness)
 
        # get the best individual of the new population and log it
        log_generation_info(iteration, time.time() - start_time, population_with_fitness, log_file)

    # return the fittest individual
    return get_n_fittest_individuals(population_with_fitness, n_best_to_return)


def main(
        mutation_prob: float, 
        crossover_prob: float,
        population_size: int, 
        generations_max: int, 
        simulations_per_indiv: int, 
        len_individual: int,
        mutation_copies: int,
        n_best_to_return: int,
        food_weight: float,
        debug: bool = False,
        ):
    
    # prepare logging file
    now = datetime.now()
    formatted_now = now.strftime("%Y-%m-%d_%H-%M-%S")
    log_file = open(f"logs/log-evolution_{formatted_now}.txt", "w")

    # run a single simulation and save the info regarding fixed parameters used in it (logging for later)
    if debug:
        log(log_file, "Evolution parameters:")
        log(log_file, str(args) + "\n")

        log(log_file, "Default simulation parameters:")
        output = subprocess.run([
            './cpp_simulation', 
            '--debug', 'true',
            '--log-filepath', f"logs/log-default-simulation_{formatted_now}.txt"
        ], stdout=subprocess.PIPE)
        output = output.stdout.decode("utf-8")
        log(log_file, output.split("Parameter values:")[1].split("Simulation starts.")[0].strip() + "\n")

        formatted_now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log(log_file, f"Starting computation at {formatted_now}.\n")

    start = time.time()

    # run the evolution
    n_best_individuals = evolution(
        mutation_prob, 
        crossover_prob,
        population_size, 
        generations_max, 
        simulations_per_indiv,
        len_individual,
        mutation_copies,
        start,
        n_best_to_return,
        food_weight,
        log_file,
        debug,
    )
    
    # sum up the results
    end = time.time()
    if debug:
        log(log_file, "\nComputation finished.")
        log(log_file, f"{n_best_to_return} best individuals of the last generation:")
        for indiv in n_best_individuals:
            log(log_file, f">>    ", end="")
            log_individual_with_fitness(indiv, log_file)
        log(log_file, f"Total time: {end - start}")  
    log_file.close()


if __name__ == "__main__":
    # parse CLI arguments

    parser = argparse.ArgumentParser(
        prog='Natural computing, project',
        description='Runs algorithm for evolution of fish swarms',
    )

    # algorithm parameters (all tunable, but with default values)
    parser.add_argument('-m', '--mutation_prob', default=0.2)
    parser.add_argument('-c', '--crossover_prob', default=0.6)
    parser.add_argument('-p', '--population_size', default=20) # ideally use 50-100?
    parser.add_argument('-g', '--generations_max', default=20) # ideally use 50-100?
    parser.add_argument('-s', '--simulations_per_indiv', default=6) # ideally use 8 or 16, depends on cores in cpu
    parser.add_argument('-l', '--len_individual', default=6)
    parser.add_argument('-f', '--food_weight', default=0.0) # TODO: decide on value, either 0 or 0.001
    parser.add_argument('-t', '--mutation_copies', default=2) # how many copies of each indiv before running mutations
    parser.add_argument('-r', '--random_seed', default=True)
    parser.add_argument('-n', '--n_best_to_return', default=10)
    parser.add_argument('-d', '--debug', default=True)
    args = parser.parse_args()

    if args.random_seed:
        random.seed(datetime.now().timestamp())
    else:
        random.seed(42)

    main(
        args.mutation_prob, 
        args.crossover_prob, 
        args.population_size, 
        args.generations_max, 
        args.simulations_per_indiv,
        args.len_individual,
        args.mutation_copies,
        args.n_best_to_return,
        args.food_weight,
        args.debug,
    )
