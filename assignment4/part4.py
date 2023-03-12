import argparse
import copy
import matplotlib.pyplot as plt
import numpy as np
import random
import string


def generate_individual(allowed_chars, target_len):
    return ''.join(random.choices(
        allowed_chars,
        weights=[1 for _ in range(len(allowed_chars))],
        k=target_len)
    )


def generate_population(allowed_chars, target_len, num_individuals):
    return [generate_individual(allowed_chars, target_len) for _ in range(num_individuals)]


def eval_fitness(individual, target):
    correct = 0
    for i in range(len(target)):
        if individual[i] == target[i]:
            correct += 1

    return correct / len(target)


def eval_population(population, target):
    return [(x, eval_fitness(x, target)) for x in population]


def get_fittest(sample_fitness_tuples):
    return max(sample_fitness_tuples, key=lambda x: x[1])


def tournament_step(population_fitness_tuples, k):
    selected_k = random.choices(population_fitness_tuples, k=k)
    return get_fittest(selected_k)


def tournament(population_fitness_tuples, k):
    selected_parents = []
    for i in range(len(population_fitness_tuples)):
        selected_parents.append(tournament_step(population_fitness_tuples, k))
    return selected_parents


def crossover(parent1, parent2):
    length = len(parent1)
    # choose the random split point
    # split idx would be the first idx from the second parent
    split_idx = random.randint(0, length - 1)

    # combine the two slices in both ways to get 2 children
    child1 = parent1[0:split_idx] + parent2[split_idx:length]
    child2 = parent2[0:split_idx] + parent1[split_idx:length]
    return child1, child2


def mutate(individual, mutation_prob, allowed_chars):
    individual_list = list(individual)
    for i in range(len(individual_list)):
        if random.uniform(0, 1) < mutation_prob:
            individual_list[i] = random.choice(allowed_chars)
    return "".join(individual_list)


def reproduce(parents, mutation_prob, allowed_chars):
    # shuffle the parents first, so that the order is 'random'
    random.shuffle(parents)

    # take pair after pair and make crossovers
    offspring_population = []
    for i in range(1, len(parents), 2):
        child1, child2 = crossover(parents[i - 1][0], parents[i][0])
        offspring_population.append(child1)
        offspring_population.append(child2)

    # apply mutations
    for i in range(len(offspring_population)):
        offspring_population[i] = mutate(offspring_population[i], mutation_prob, allowed_chars)

    return offspring_population


def main(
    allowed_chars,
    target_str,
    target_len,
    num_individuals,
    mutation_prob,
    tournament_k,
    max_iterations=None,
):
    if target_str is None:
        target_str = generate_individual(allowed_chars, target_len)
    print(f"TARGET:  \'{target_str}\'")

    # generate the population and evaluate it
    population = generate_population(allowed_chars, target_len, num_individuals)
    population_fitness_tuples = eval_population(population, target_str)

    # stopping condition and progress check variables
    iter_num = 0
    best_individual = get_fittest(population_fitness_tuples)
    target_found = best_individual[0] == target_str
    stop_condition = target_found or (max_iterations is not None and iter_num == max_iterations)

    while not stop_condition:
        # TODO: select parents using tournament
        new_parents = tournament(population_fitness_tuples, tournament_k)

        # TODO: generate N new offsprings (do crossovers and mutations)
        offspring_population = reproduce(new_parents, mutation_prob, allowed_chars)

        # TODO: replace generations and evaluate the new individuals
        population_fitness_tuples = eval_population(offspring_population, target_str)

        # get the best individual of the new population
        best_individual = get_fittest(population_fitness_tuples)
        print(f"ITERATION {iter_num}:   {best_individual}")

        # update stop condition
        iter_num += 1
        target_found = best_individual[0] == target_str
        stop_condition = target_found or (max_iterations is not None and iter_num == max_iterations)


if __name__ == "__main__":
    # parse CLI arguments

    parser = argparse.ArgumentParser(
        prog='Natural computing, Assignment 4, part 4',
        description='Runs genetic algorithm for string matching',
    )
    # algorithm parameters
    parser.add_argument('-m', '--mutation_prob', default=0.01)
    parser.add_argument('-k', '--k_tournament', default=2)
    parser.add_argument('-n', '--n_population', default=1000)
    parser.add_argument('-l', '--length_target', default=15)
    parser.add_argument('-t', '--target', default=None)
    parser.add_argument('-g', '--g_max', default=1000)
    args = parser.parse_args()

    alphabet = string.ascii_lowercase + " "
    assert len(alphabet) == 27

    if args.target is not None:
        assert len(args.target) == args.length_target

    random.seed(10)  # include if replicability needed

    main(alphabet, args.target, args.length_target, args.n_population, args.mutation_prob, args.k_tournament, args.g_max)
