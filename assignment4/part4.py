import argparse
from datetime import datetime
import seaborn as sns
import numpy as np
import random
import string
import pandas as pd


def generate_individual(allowed_chars, target_len):
    """Randomly generate an individual of size `target_len`."""
    return ''.join(random.choices(
        allowed_chars,
        weights=[1 for _ in range(len(allowed_chars))],
        k=target_len)
    )


def generate_population(allowed_chars, target_len, num_individuals):
    """Randomly generate whole population of size `num_individuals`."""
    return [generate_individual(allowed_chars, target_len) for _ in range(num_individuals)]


def eval_fitness(individual, target):
    """Evaluate fitness of an `individual` as fraction of 'correct' characters wrt. `target`."""
    correct = 0
    for i in range(len(target)):
        if individual[i] == target[i]:
            correct += 1

    return correct / len(target)


def eval_population(population, target):
    """Evaluate fitness of whole population, return list of tuples <individual, fitness>."""
    return [(x, eval_fitness(x, target)) for x in population]


def get_fittest(sample_fitness_tuples):
    """Return the fittest individual from the population."""
    return max(sample_fitness_tuples, key=lambda x: x[1])


def tournament_step(population_fitness_tuples, k):
    """Randomly select `k` individuals and take the best one."""
    selected_k = random.choices(population_fitness_tuples, k=k)
    return get_fittest(selected_k)


def tournament(population_fitness_tuples, k):
    """
    Select parents for reproduction using tournament selection.
    To get N offsprings, we will need N parents (N is population size).
    """
    selected_parents = []
    for i in range(len(population_fitness_tuples)):
        selected_parents.append(tournament_step(population_fitness_tuples, k))
    return selected_parents


def crossover(parent1, parent2):
    """Do a random point crossover of the 2 parents, return both children."""
    length = len(parent1)
    # choose the random split point
    # split idx would be the first idx from the second parent
    split_idx = random.randint(0, length - 1)

    # combine the two slices in both ways to get 2 children
    child1 = parent1[0:split_idx] + parent2[split_idx:length]
    child2 = parent2[0:split_idx] + parent1[split_idx:length]
    return child1, child2


def mutate(individual, mutation_prob, allowed_chars):
    """Mutate the given `individual`."""
    individual_list = list(individual)
    for i in range(len(individual_list)):
        if random.uniform(0, 1) < mutation_prob:
            # randomly select the substitution character
            individual_list[i] = random.choice(allowed_chars)
    return "".join(individual_list)


def reproduce(parents, mutation_prob, allowed_chars):
    """Generate new offspring generation from parents by applying crossover and mutations."""
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


def genetic_algo(
    allowed_chars,
    target_str,
    num_individuals,
    mutation_prob,
    tournament_k,
    max_iterations=None,
    debug=False,
):
    """Run the whole genetic algorithm."""

    assert target_str is not None

    # generate the population and evaluate it
    population = generate_population(allowed_chars, len(target_str), num_individuals)
    population_fitness_tuples = eval_population(population, target_str)

    # initialize stopping condition and progress check variables
    iter_num = 1
    best_individual = get_fittest(population_fitness_tuples)
    target_found = best_individual[0] == target_str
    stop_condition = target_found

    while not stop_condition:
        # select parents using tournament
        new_parents = tournament(population_fitness_tuples, tournament_k)

        # generate N new offsprings (do the crossovers and mutations)
        offspring_population = reproduce(new_parents, mutation_prob, allowed_chars)

        # replace generations and evaluate the new individuals
        population_fitness_tuples = eval_population(offspring_population, target_str)

        # get the best individual of the new population
        best_individual = get_fittest(population_fitness_tuples)
        if debug:
            print(f"ITERATION {iter_num}:   {best_individual}")

        # update stop condition
        iter_num += 1
        target_found = best_individual[0] == target_str
        stop_condition = target_found or (max_iterations is not None and iter_num > max_iterations)

    return target_found, iter_num - 1


def run_experiment(
    num_runs,
    allowed_chars,
    target_str,
    num_individuals,
    mutation_prob,
    tournament_k,
    max_iterations,
    debug=False,
):
    """
    Run the genetic algorithm `num_runs` times with the same parameters.
    For each run, save information regarding:
        1) if the target was found or G_max was reached
        2) the number of iterations needed to get the target (if found)
    Plot the distribution of iteration numbers, and print stats.
    """

    if debug:
        print(f"TARGET:  \'{target_str}\'")
        print(f"M:  {mutation_prob}")
        print(f"K:  {tournament_k}")
        print()

    found_list = []
    num_iterations_list = []
    for i in range(num_runs):
        found, num_iterations = genetic_algo(
            allowed_chars,
            target_str,
            num_individuals,
            mutation_prob,
            tournament_k,
            max_iterations,
        )
        found_list.append(found)
        num_iterations_list.append(num_iterations)
        if debug:
            print(f"RUN {i+1} | iterations: {num_iterations}, found: {found}")

    if debug:
        print("\n----------OVERALL STATS----------\n")
        print("found:", found_list)
        print("iterations:", num_iterations_list)
        print(f"number of found: {found_list.count(True)} (out of {num_runs})")

    # filter only to those that represent successful runs
    num_iterations_list = [num_iterations_list[i] for i in range(num_runs) if found_list[i]]
    num_iter_mean = sum(num_iterations_list) / len(num_iterations_list) if num_iterations_list else None
    num_iter_std = np.std(num_iterations_list) if num_iterations_list else None

    if debug:
        print("iterations (if found):", num_iterations_list)
        print("iterations mean (if found):", num_iter_mean)
        print("iterations std (if found):", num_iter_std)

        # plot distribution of iteration numbers
        max_iter = max(num_iterations_list)
        min_iter = min(num_iterations_list)
        # add few more bins on sides
        max_iter = max_iter + max_iter // 10
        min_iter = max(0, min_iter - 10)
        sns.set(rc={'figure.figsize': (12, 8)})
        sns.displot(num_iterations_list, bins=list(range(min_iter, max_iter+10))).figure.savefig("output.png")

    return found_list.count(True), num_iter_mean, num_iter_std


def get_step_size(m_value, current_step, scheme):
    step = current_step
    if scheme and m_value >= scheme[0][0]:
        step = scheme[0][1]
        scheme.pop(0)
    return step


def run_experiments_with_different_m(
    num_runs,
    allowed_chars,
    target_str,
    num_individuals,
    tournament_k,
    max_iterations,
    max_m=0.2,
    update_scheme=None,
):
    """
    Run several experiments with different values of M.
    For each experiment, save information regarding:
        1) number of successful runs
        2) the mean and std of iterations needed for successful runs
    Plot the relationship between M & iterations mean, and M & iterations std.
    """

    print(f"TARGET:  \'{target_str}\'")
    print(f"K:  {tournament_k}")
    print()

    current_m = 0
    # get the init step size from the update scheme
    step_m = update_scheme[0][1]
    update_scheme.pop(0)

    map_m_to_results = dict()
    m_with_best_mean = (0, max_iterations, max_iterations)
    while current_m <= max_m:
        found_num, mean_iter, std_iter = run_experiment(
            num_runs,
            allowed_chars,
            target_str,
            num_individuals,
            current_m,
            tournament_k,
            max_iterations,
        )

        # save results
        map_m_to_results[current_m] = (found_num, mean_iter, std_iter)

        if found_num > 0:
            print(f"M = {current_m:.4f} | found: {found_num}, mean found: {mean_iter:.2f}, std found: {std_iter:.2f}")
        else:
            print(f"M = {current_m:.4f} | found: 0, mean found: -, std found: -")

        # only update best if all targets were found
        if found_num == num_runs:
            # update if mean better, or mean is same and std is better
            if mean_iter < m_with_best_mean[1]:
                m_with_best_mean = (current_m, mean_iter, std_iter)
            elif mean_iter == m_with_best_mean[1] and std_iter < m_with_best_mean[2]:
                m_with_best_mean = (current_m, mean_iter, std_iter)

        # check and potentially update the step size before incrementing
        step_m = get_step_size(current_m, step_m, update_scheme)
        current_m += step_m

    print(map_m_to_results)
    print(f"BEST: M={m_with_best_mean[0]}, mean={m_with_best_mean[1]}, std={m_with_best_mean[2]}")


def make_a_plot():
    """Use pre-computed values to make a plot. Pre-computed values are used because of the computation length"""

    m_vals_k5 = [0.0000, 0.0001, 0.0002, 0.0003, 0.0004, 0.0005, 0.0006, 0.0007, 0.0008, 0.0009, 0.0010, 0.0020, 0.0030, 0.0040, 0.0050, 0.0060, 0.0070, 0.0080, 0.0090, 0.0100, 0.0200, 0.0300, 0.0400, 0.0500, 0.0600, 0.0700, 0.0800, 0.0900, 0.1000, 0.1200, 0.1400, 0.1600, 0.1800, 0.2000, 0.2200]

    # values for K=2
    mean_vals_k2 = [17.70, 17.40, 17.90, 17.55, 18.25, 18.00, 17.50, 17.85, 17.85, 17.65, 17.95, 17.85, 18.00, 18.30, 18.10, 18.15, 18.10, 18.65, 18.00, 18.65, 20.05, 20.55, 21.05, 23.85, 25.55, 29.00, 34.20, 41.80, 71.15, 191.20]
    std_vals_k2 = [1.00, 1.07, 0.89, 1.32, 0.99, 1.22, 1.12, 1.06, 1.28, 1.24, 1.47, 1.01, 1.22, 1.19, 1.30, 1.06, 1.26, 1.28, 1.52, 1.15, 1.66, 1.86, 2.06, 1.65, 2.06, 3.59, 5.78, 6.59, 23.90, 203.60]

    # values for K=5
    mean_vals_k5 = [10.10, 10.20, 9.85, 10.25, 10.00, 10.50, 10.30, 10.25, 10.25, 10.10, 10.20, 10.35, 10.00, 10.30, 10.40, 10.30, 9.95, 10.20, 10.55, 10.45, 10.75, 11.05, 11.05, 11.45, 11.30, 12.40, 12.75, 12.75, 13.25, 14.10, 16.35, 19.85, 25.40, 50.05, 271.85]
    std_vals_k5 = [0.77, 0.40, 0.79, 0.77, 0.84, 0.67, 0.90, 0.70, 0.70, 0.77, 0.68, 0.65, 0.84, 0.78, 0.66, 0.64, 0.74, 0.87, 1.12, 1.40, 0.89, 0.67, 1.24, 1.12, 1.00, 0.86, 1.09, 1.34, 1.22, 1.48, 1.88, 3.07, 5.79, 21.96, 184.14]

    mean_frame = pd.DataFrame({
        "M": m_vals_k5,
        "Mean generations for K = 2": [(mean_vals_k2[i] if i < len(mean_vals_k2) else None) for i in range(len(m_vals_k5))],
        "Mean generations for K = 5": mean_vals_k5,
    })

    std_frame = pd.DataFrame({
        "M": m_vals_k5,
        "Std of generations n. for K = 2": [(std_vals_k2[i] if i < len(std_vals_k2) else None) for i in range(len(m_vals_k5))],
        "Std of generations n. for K = 5": std_vals_k5,
    })

    # create scatterplot with log scale on y-axis
    sns.set(rc={'figure.figsize': (12, 8)})
    p = sns.lineplot(x="M", y="value", hue="variable", data=pd.melt(std_frame, ['M']))

    import matplotlib.pyplot as plt
    plt.xscale('log')
    p.figure.savefig("output.png")


if __name__ == "__main__":
    # parse CLI arguments

    parser = argparse.ArgumentParser(
        prog='Natural computing, Assignment 4, part 4',
        description='Runs genetic algorithm for string matching',
    )
    # algorithm parameters (make them all tunable, but with default values)
    parser.add_argument('-m', '--mutation_prob', default=0.01)
    parser.add_argument('-k', '--k_tournament', default=2)
    parser.add_argument('-n', '--n_population', default=1000)
    parser.add_argument('-l', '--length_target', default=15)
    parser.add_argument('-t', '--target', default="abcdefghijklmno")
    parser.add_argument('-g', '--g_max', default=1000)
    parser.add_argument('-r', '--runs_number', default=20)
    args = parser.parse_args()

    # the alphabet is comprised of ASCII lowercase letters + a space
    alphabet = string.ascii_lowercase + " "
    assert len(alphabet) == 27

    random.seed(random.seed(datetime.now().timestamp()))  # include if randomness needed
    # random.seed(10)                                     # include if replicability needed

    # generate target randomly if none given (for debugging purposes)
    target = args.target
    if target is not None:
        assert len(target) == args.length_target
    else:
        target = generate_individual(args.allowed_chars, args.target_len)

    # UNCOMMENT this for experiments with fixed M
    """
    run_experiment(
        args.runs_number,
        alphabet,
        target,
        args.n_population,
        args.mutation_prob,
        args.k_tournament,
        args.g_max,
        debug=True,
    )
    """

    # UNCOMMENT this for experiments with M-search
    """
    # update step schedule - start with tiny updates, make larger when hitting certain thresholds
    step_update_scheme = [
        (0, 0.0001),
        (0.001, 0.001),
        (0.01, 0.01),
        (0.1, 0.02),
        (0.3, 0.05),
    ]
    run_experiments_with_different_m(
        args.runs_number,
        alphabet,
        target,
        args.n_population,
        args.k_tournament,
        args.g_max,
        max_m=0.4,
        update_scheme=step_update_scheme,
    )
    """

    # UNCOMMENT this for plotting M-search
    """
    make_a_plot()
    """
