import numpy as np
from Parameters import Configuration


def ES_Step(theta, E, args, in_place=False):
    og_weights = theta.get_weights()

    shared_gaussian_table = [np.random.normal(0, 1, size=len(og_weights)) for i in range(args.batch_size)]

    thetas = []
    for i in range(args.batch_size):
        new_theta = Configuration.agentFactory.new()
        new_theta.set_weights(og_weights + args.sigma * shared_gaussian_table[i])
        thetas.append(new_theta)

    scores = Configuration.lview.map(E, thetas)
    scores = np.array(scores)
    print(scores.max())
    for i in range(len(scores)):
        scores[i] -= args.l_decay * np.linalg.norm(og_weights + args.sigma * shared_gaussian_table[i])
       
    scores = rank_normalize(scores)
    Configuration.budget_spent[-1] += len(thetas)
    
    summed_weights = np.zeros(og_weights.shape)
    for i in range(len(scores)):
        summed_weights += scores[i] * shared_gaussian_table[i]
    new_weights = args.alpha * (1.0/(len(shared_gaussian_table)*args.sigma)) * summed_weights
    print(new_weights.mean())
    new_weights += og_weights

    if in_place:
        theta.set_weights(new_weights)
        return

    theta.set_weights(og_weights)
    new_ag = Configuration.agentFactory.new()
    new_ag.set_weights(new_weights)
    return new_ag
    
def rank_normalize(arr):
    sorted = arr.argsort()
    return sorted / sorted.max()