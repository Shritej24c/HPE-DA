
# genetic algorithm search for continuous function optimization
import selection as selection
import numpy as np
from numpy.random import randint
from numpy.random import rand

from random import choices, randint, randrange, random
from typing import List, Optional, Callable, Tuple

Genome = List[int]
Population = List[Genome]
PopulateFunc = Callable[[], Population]
FitnessFunc = Callable[[Genome], int]
SelectionFunc = Callable[[Population, FitnessFunc], Tuple[Genome, Genome]]
CrossoverFunc = Callable[[Genome, Genome], Tuple[Genome, Genome]]
MutationFunc = Callable[[Genome], Genome]
PrinterFunc = Callable[[Population, int, FitnessFunc], None]


def regressor(x):
    return output


# objective function
def objective(x, gamma):
    for i in x:
        if (50 > bin_to_int(i) > 2) & (check_sum(x) == 0):
            return regressor(x)
        else:
            return min(regressor(x) - gamma*check_sum(x)**2, 0)


def generate_genome(num_numbers, total_sum, min_val, max_val) -> Genome:
    numbers = []
    while len(numbers) < num_numbers - 1:
        num = randint(min_val, max_val)
        if total_sum - sum(numbers) - num >= min_val * (num_numbers - len(numbers) - 1):
            numbers.append(num)
    numbers.append(total_sum - sum(numbers))
    binary_numbers = []  # This will store the binary representation of each number

    for number in numbers:
        binary = bin(number)[2:]  # Convert the number to binary and remove the '0b' prefix
        binary_list = [int(bit) for bit in binary.zfill(7)]  # Convert the binary string to a list of integers
        binary_numbers.append(binary_list)
    return binary_numbers


def generate_genome2(num_numbers, total_sum, min_val, max_val) -> Genome:
    numbers = []
    while len(numbers) < num_numbers - 1:
        num = randint(min_val, min(max_val, total_sum - sum(numbers)))
        numbers.append(num)
    numbers.append(total_sum - sum(numbers))
    binary_numbers = []  # This will store the binary representation of each number

    for number in numbers:
        binary = int_to_bin(number)  # Convert the number to binary and remove the '0b' prefix
        binary_numbers.append(binary)
    return binary_numbers


def int_to_bin(num):
    binary = bin(num)[2:]  # Convert the number to binary and remove the '0b' prefix
    binary_list = [int(bit) for bit in binary.zfill(7)]  # Convert the binary string to a list of integers
    return binary_list


def bin_to_int(num):
    s = ''
    for i in num:
        s += str(i)
    return int(s, 2)


def check_sum(genome):
    tot = 0
    for v in genome:
        tot += bin_to_int(v)
        # Slack variable
    return tot - 100


def repair(genome: Genome,  alpha: int, method=("greedy", 'conservative')) -> Genome:
    diff = check_sum(genome)
    new_gene = sorted(genome, key=lambda x: bin_to_int(x))
    if 0 < diff < alpha:
        if method == 'greedy':
            i = 0
            while diff >0:
                new_gene[i] = int_to_bin(bin_to_int(new_gene[i]) -1)
                i += 1
                diff -= 1
        elif method == 'conservative':
            while diff > 0:
                i = randint(0, len(new_gene))
                new_gene[i] = int_to_bin(bin_to_int(new_gene[i]) - 1)
                diff -= 1
    elif -alpha < diff < 0:
        ng = new_gene[::-1]
        if method == "greedy":
            i = 0
            while diff < 0:
                ng[i] = int_to_bin(bin_to_int(ng[i]) + 1)
                i += 1
                diff += 1
        elif method == 'conservative':
            while diff < 0:
                i = randint(0, len(new_gene))
                ng[i] = int_to_bin(bin_to_int(ng[i]) + 1)
                diff += 1
    return new_gene


def generate_population(size: int, num_numbers: int, total_sum: int, min_val: int) -> Population:
    pop = list()
    for _ in range(size):
        max_value = random.randint(9,20)
        genome_gen = generate_genome(num_numbers, total_sum, min_val, max_value)
        pop.append(genome_gen)
    return pop


def selection_pair(population: Population, fitness_func: FitnessFunc) -> Population:
    return choices(
        population=population,
        weights=[fitness_func(gene) for gene in population],
        k=2
    )


def xnor(bit1, bit2):
    return ~(bit1 ^ bit2) & 1


# crossover two parents to create two children
def crossover(p1, p2, r_cross, alpha, method = ('1point', '2point', 'uniform', 'operator1', 'operator2')):
    # children are copies of parents by default
    c1, c2 = p1.copy(), p2.copy()
    # check for recombination
    if rand() < r_cross:
        if method == '1point':
            # select crossover point that is not on the end of the string
            pt = randint(1, len(p1) - 2)
            # perform crossover
            c1 = p1[:pt] + p2[pt:]
            c2 = p2[:pt] + p1[pt:]
        elif method == '2point':
            p = sorted(random.sample(range(1, len(p1)), 2))

            # Create offspring chromosomes by combining parts of the parents
            c1 = p1[:p[0]] + p2[p[0]:p[1]] + p1[ p[1]:]
            c2 = p2[:p[0]] + p1[p[0]:p[1]] + p2[p[1]:]

        elif method == 'uniform':
            for i in range(len(p1)):
                if random.random() < 0.5:
                    c1 += p1[i]
                    c2 += p2[i]
                else:
                    c1 += p2[i]
                    c2 += p1[i]

        elif method == 'operator1':
            for i in range(len(p1)):
                c1[i] = int_to_bin(bin_to_int(p1[i]) ^ bin_to_int(p2[i])) #XOR
                c2[i] = int_to_bin(bin_to_int(p1[i]) | bin_to_int(p2[i])) #OR
        elif method == 'operator2':
            for i in range(len(p1)):
                c1[i] = int_to_bin(~(bin_to_int(p1[i]) ^ bin_to_int(p2[i]))) #XAND
                c2[i] = int_to_bin(bin_to_int(p1[i]) & bin_to_int(p2[i]))  #AND

        if (abs(check_sum(c1)) > alpha) or ( abs(check_sum(c2)) > alpha):
            l = ['1point', '2point', 'uniform', 'operator1', 'operator2']
            l.remove(method)
            method = choices(l)
            [c1, c2] = crossover(p1, p2, r_cross, method, alpha)

        elif 0 < abs(check_sum(c1)) < alpha:
            c1 = repair(c1, method='greedy')

        elif 0 < abs(check_sum(c2)) < alpha:
            c2 = repair(c2, method='greedy')

    return [c1, c2]


def population_fitness(population: Population, fitness_func: FitnessFunc) -> int:
    return sum([fitness_func(genome) for genome in population])


def sort_population(population: Population, fitness_func: FitnessFunc) -> Population:
    return sorted(population, key=fitness_func, reverse=True)


def genome_to_string(genome: Genome) -> str:
    return "".join(map(str, genome))


def mutation(genome: Genome, alpha, num: int = 1, probability: float = 0.5) -> Genome:
    for _ in range(num):
        index = randrange(len(genome))
        genome[index] = genome[index] if random() > probability else abs(genome[index] - 1)

    if abs(check_sum(genome)) > alpha  :
        genome = mutation(genome, alpha, num, probability)

    elif 0 < abs(check_sum(genome)) < alpha:
        genome = repair(genome, method='greedy')

    return genome


def print_stats(population: Population, generation_id: int, fitness_func: FitnessFunc):
    print("GENERATION %02d" % generation_id)
    print("=============")
    print("Population: [%s]" % ", ".join([genome_to_string(gene) for gene in population]))
    print("Avg. Fitness: %f" % (population_fitness(population, fitness_func) / len(population)))
    sorted_population = sort_population(population, fitness_func)
    print(
        "Best: %s (%f)" % (genome_to_string(sorted_population[0]), fitness_func(sorted_population[0])))
    print("Worst: %s (%f)" % (genome_to_string(sorted_population[-1]),
                              fitness_func(sorted_population[-1])))
    print("")

    return sorted_population[0]


def run_evolution(
        populate_func: PopulateFunc,
        fitness_func: FitnessFunc,
        fitness_limit: int,
        selection_func: SelectionFunc = selection_pair,
        crossover_func: CrossoverFunc = crossover,
        mutation_func: MutationFunc = mutation,
        generation_limit: int = 100,
        printer: Optional[PrinterFunc] = None) \
        -> Tuple[Population, int]:
    population = populate_func()

    for i in range(generation_limit):
        population = sorted(population, key=lambda genome: fitness_func(genome), reverse=True)

        if printer is not None:
            printer(population, i, fitness_func)

        if fitness_func(population[0]) >= fitness_limit:
            break

        next_generation = population[0:2]

        for j in range(int(len(population) / 2) - 1):
            parents = selection_func(population, fitness_func)
            offspring_a, offspring_b = crossover_func(parents[0], parents[1])
            offspring_a = mutation_func(offspring_a)
            offspring_b = mutation_func(offspring_b)
            next_generation += [offspring_a, offspring_b]

        population = next_generation

    return population, i




'''

# genetic algorithm
def genetic_algorithm(objective, bounds, n_bits, n_iter, n_pop, r_cross, r_mut):
     # initial population of random bitstring
     pop = [randint(0, 2, n_bits * len(bounds)).tolist() for _ in range(n_pop)]
      # keep track of best solution
     best, best_eval = 0, objective(decode(bounds, n_bits, pop[0]))
     # enumerate generations
     for gen in range(n_iter):
    # decode population
         decoded = [decode(bounds, n_bits, p) for p in pop]
  # evaluate all candidates in the population
         scores = [objective(d) for d in decoded]
  # check for new best solution
     for i in range(n_pop):
         if scores[i] < best_eval:
             best, best_eval = pop[i], scores[i]
             print(">%d, new best f(%s) = %f" % (gen, decoded[i], scores[i]))
             # select parents
     selected = [selection(pop, scores) for _ in range(n_pop)]
     # create the next generation
     children = list()
     for i in range(0, n_pop, 2):
     # get selected parents in pairs
        p1, p2 = selected[i], selected[i + 1]
        # crossover and mutation
        for c in crossover(p1, p2, r_cross):
         # mutation
            mutation(c, r_mut)
 # store for next generation
     children.append(c)
     # replace population
     pop = children
     return [best, best_eval]





# define range for input
bounds = [[2, 50] for i in range(15)]
# define the total iterations
n_iter = 100
# bits per variable
n_bits = 7
# define the population size
n_pop = 100
# crossover rate
r_cross = 0.9
# mutation rate
r_mut = 1.0 / (float(n_bits) * len(bounds))
# perform the genetic algorithm search

# initial population of random bitstring
pop = [randint(0, 2, n_bits*len(bounds)).tolist() for _ in range(n_pop)]


best, score = genetic_algorithm(objective, bounds, n_bits, n_iter, n_pop, r_cross, r_mut)
print('Done!')
decoded = decode(bounds, n_bits, best)
print('f(%s) = %f' % (decoded, score))


'''
