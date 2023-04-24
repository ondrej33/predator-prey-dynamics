import argparse
from datetime import datetime
import random


def generate_individual():
    """Randomly generate an individual of size `target_len`."""
    # TODO
    pass



def generate_population():
    """Randomly generate whole population of size `num_individuals`."""
    # TODO
    pass


def eval_individual():
    """Evaluate fitness of an `individual`"""
    # TODO
    pass


def eval_population():
    """Evaluate fitness of whole population, return list of tuples <individual, fitness>."""
    # TODO
    pass


def get_fittest_individual():
    """Return the fittest individual from the population."""
    # TODO
    pass


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
    debug=False,
):
    """Run the whole evolution process."""

    # TODO: generate the population and evaluate it
    generate_population()
    eval_population()

    # TODO: initialize stopping condition and progress check variables
    iteration = 0
    stop_condition = generations_max == iteration

    while not stop_condition:
        # TODO: select parents from the population
        selection_step()

        # TODO: generate new offspring set (do the crossovers and mutations)
        reproduction_step()

        # TODO: replace generations and evaluate the new individuals
        replacement_step()

        # TODO: get the best individual of the new population and log it
        get_fittest_individual()

        # TODO: update stop condition
        stop_condition = generations_max == iteration

    pass


def main(mutation_prob, population_size, generations_max, simulations_per_indiv, debug=False):
    # TODO: prepare some things
    
    # TODO: run evolution
    evolution(
        mutation_prob, 
        population_size, 
        generations_max, 
        simulations_per_indiv,
        debug,
    )
    
    # TODO: sum up results
    pass


if __name__ == "__main__":
    # parse CLI arguments

    parser = argparse.ArgumentParser(
        prog='Natural computing, project',
        description='Runs algorithm for evolution of fish swarms',
    )

    # algorithm parameters (all tunable, but with default values)
    parser.add_argument('-m', '--mutation_prob', default=0.02)
    parser.add_argument('-p', '--population_size', default=100)
    parser.add_argument('-g', '--generations_max', default=1000)
    parser.add_argument('-s', '--simulations_per_indiv', default=10)
    parser.add_argument('-r', '--random_seed', default=False)
    parser.add_argument('-d', '--debug', default=True)
    args = parser.parse_args()

    if args.random_seed:
        random.seed(random.seed(datetime.now().timestamp()))
    else:
        random.seed(42)

    main(
        args.mutation_prob, 
        args.population_size, 
        args.generations_max, 
        args.simulations_per_indiv,
        args.debug,
    )
