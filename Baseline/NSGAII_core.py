import numpy as np
import random
from Parameters import Configuration


def fast_non_dominated_sort(elements):
    """
    Fast non-dominated sort in the sens of Pareto, as in the original NSGA-II algorithm.
    :param elements: array (m, n) of n objectives for m agents.
    :return: front ranks as a list.
    """
    S = [list() for i in range(len(elements))]
    n = [0 for i in range(len(elements))]
    f_i = list()

    ranks = [0 for i in range(len(elements))]

    for p in range(len(elements)):
        for q in range(len(elements)):
            if dominates(elements[p], elements[q]):
                S[p].append(q)
            elif dominates(elements[q], elements[p]):
                ranks[p] = 1
                n[p] += 1
        if n[p] == 0:
            f_i.append(p)

    i = 0
    f_i = f_i
    while len(f_i) != 0:
        Q = list()
        for p in f_i:
            for q in S[p]:
                n[q] -= 1
                if n[q] == 0:
                    ranks[q] = i + 1
                    Q.append(q)
        i += 1
        f_i = Q
    return ranks


def dominates(a, b):
    """Return true if a Pareto dominates b (maximization)"""
    equals = True
    for i in range(len(a)):
        equals = equals and a[i] == b[i]
        if a[i] < b[i]:
            return False
    if equals:
        return False
    return True


def crowding_distance(elements):
    """elements is expected to be an array (m, n) of n objectives for m agents"""
    distance = [0 for i in range(len(elements))]
    for i in range(len(elements[0])):
        sorted_elements = sorted(elements, key=lambda x: x[i])
        sorted_args = sorted(range(len(elements)), key=lambda x: elements[x][i])
        distance[sorted_args[0]] = float("inf")
        distance[sorted_args[-1]] = float("inf")
        maxi = sorted_elements[-1][i]
        mini = sorted_elements[0][i]
        for k in range(1, len(elements) - 1):
            distance[sorted_args[k]] += (sorted_elements[k + 1][i] - sorted_elements[k - 1][i]) / (maxi - mini)
    return distance


def new_population(old_learners, args):
    """
    Create a new agent population from a parent one.
    If the parent population does not contain any agent, returns a new random one.
    The strategy is mutation with probability p1, crossover with probability p2, random agent with probability 1-p1-p2.
    Mutants and crossover parents are chosen with equal probability from the parent list.

    :param old_learners: parent agent population
    :param args: argparse object
    :return: agent population as a list
    """
    # Mutation, reproduction & new ones
    new_learners = list()
    for i in range(args.gen_size):
        action = np.random.random()
        if len(old_learners) == 0:
            action = 1  # Ensure new agents only if there are currently no agents
        if action < args.p_mut_ag:
            new_learners.append(mutate_ag(old_learners[np.random.randint(0, len(old_learners))], args))
        elif action < args.p_cross_ag:
            choices = np.random.choice(np.arange(len(old_learners)), 2)
            new_learners.append(mate_ag(old_learners[choices[0]], old_learners[choices[1]], args))
        else:
            new = Configuration.agentFactory.new()
            new.randomize()
            new_learners.append(new)
    return new_learners


def mutate_ag(agent, args):
    if Configuration.benchmark is not None:
        return mutPolynomialBounded(agent, args.eta_mut, -100, 100, args.p_mut_gene)
    return mutPolynomialBounded(agent, args.eta_mut, -1, 1, args.p_mut_gene)

    # # Uniform mutation
    # new_wei = agent.get_weights()
    # for i in range(len(new_wei)):
    #     if np.random.random() < args.p_mut_gene:
    #         new_wei[i] += np.random.uniform(-1, 1) * args.mut_step
    # new = Configuration.agentFactory.new()
    # new.set_weights(new_wei)
    # return new


def mate_ag(agent1, agent2, args):
    return cxSimulatedBinary(agent1, agent2, args.eta_cross)

    # # Uniform crossover
    # wei_1 = agent1.get_weights()
    # wei_2 = agent2.get_weights()
    # new_wei = list()
    # for i in range(len(wei_1)):
    #     if np.random.random() < 0.5:
    #         new_wei.append(wei_1[i])
    #     else:
    #         new_wei.append(wei_2[i])
    # new = Configuration.agentFactory.new()
    # new.set_weights(new_wei)
    # return new


def mutPolynomialBounded(individual, eta, low, up, indpb):
    """
    Polynomial mutation as implemented in original NSGA-II algorithm in
    C by Deb, returns a new agent.
    This function is in parts taken from the DEAP package for python.
    """
    weights = individual.get_weights()
    size = len(weights)
    xl = low
    xu = up
    for i in range(size):
        if random.random() <= indpb:
            x = weights[i]
            delta_1 = (x - xl) / (xu - xl)
            delta_2 = (xu - x) / (xu - xl)
            rand = random.random()
            mut_pow = 1.0 / (eta + 1.)

            if rand < 0.5:
                xy = 1.0 - delta_1
                val = 2.0 * rand + (1.0 - 2.0 * rand) * xy ** (eta + 1)
                delta_q = val ** mut_pow - 1.0
            else:
                xy = 1.0 - delta_2
                val = 2.0 * (1.0 - rand) + 2.0 * (rand - 0.5) * xy ** (eta + 1)
                delta_q = 1.0 - val ** mut_pow

            x = x + delta_q * (xu - xl)
            x = min(max(x, xl), xu)
            weights[i] = x
    new = Configuration.agentFactory.new()
    new.set_weights(weights)
    return new


def cxSimulatedBinary(ind1, ind2, eta):
    """
    Executes a simulated binary crossover, returns a new agent.
    This function is in parts taken from the DEAP package for python.
    """
    w1 = ind1.get_weights()
    w2 = ind2.get_weights()
    for i, (x1, x2) in enumerate(zip(w1, w2)):
        rand = random.random()
        if rand <= 0.5:
            beta = 2. * rand
        else:
            beta = 1. / (2. * (1. - rand))
        beta **= 1. / (eta + 1.)
        w1[i] = 0.5 * (((1 + beta) * x1) + ((1 - beta) * x2))

    new = Configuration.agentFactory.new()
    new.set_weights(w1)
    return new


if __name__ == "__main__":
    Configuration.make()
    for k in range(50):
        ag = Configuration.agentFactory.new()

        ag2 = mutPolynomialBounded(ag, 0.5, -1, 1, 1)
        ag3 = cxSimulatedBinary(ag, ag2, 0.5)

        print(ag.get_weights())
        print(ag2.get_weights())
        print(ag3.get_weights())
    # vals = [[10, 0], [0, 10], [5, 5], [4, 2], [4, 4], [8, 2]]
    # import matplotlib.pyplot as plt
    # for v in vals:
    #     plt.plot(v[0], v[1], "o")
    # plt.show()
    # print(crowding_distance(vals))
