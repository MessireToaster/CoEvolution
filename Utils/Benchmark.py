import numpy as np
from Parameters import Configuration


def gramacy_lee(x):
    res = (10*x-1)**4 + np.sin(100*np.pi*x)/(2*(10*x))
    return res


def custom(x):
    res = 1.2*np.cos(8.0*(x-1)) - 0.1*(x-1)**2
    return res


class Benchmark:

    max_id = 0

    def __init__(self, config, iden=-1):
        size, maximum, argmax = config
        self.benchmark_frequency = np.ones(size)
        self.benchmark_offset = np.zeros(size)
        self.size = size
        self.max = maximum
        self.argmax = argmax

        if iden == -1:
            self.id = Benchmark.max_id
            Benchmark.max_id += 1
        else:
            self.id = iden
        self.parent_list = []

    def __call__(self, agent, render=False, max_steps=2000, exceed_reward=0):
        wei = agent.get_weights()
        res = 0
        for i in range(len(wei)):
            value = Configuration.benchmark(self.benchmark_frequency[i] * wei[i] + self.benchmark_offset[i])
            res += value / self.max
        return 100.0 * res / len(wei)

    def get_child(self):
        child = Benchmark((self.size, self.max, self.argmax))
        child.benchmark_frequency = self.benchmark_frequency + np.random.uniform(-0.1, 0.1, size=self.size)
        child.benchmark_offset = self.benchmark_offset + np.random.uniform(-0.1, 0.1, size=self.size)
        child.parent_list.append((self.id,))
        return child

    def mate(self, other):
        child = Benchmark((self.size, self.max, self.argmax))
        child.benchmark_frequency = (self.benchmark_frequency + other.benchmark_frequency)/2.0
        child.benchmark_offset = (self.benchmark_offset + other.benchmark_offset)/2.0
        child.parent_list.append((self.id, other.id))
        return child

    def __getstate__(self):
        dic = dict()
        dic["Freq"] = self.benchmark_frequency.tolist()
        dic["Offset"] = self.benchmark_offset.tolist()
        dic["size"] = self.size
        dic["max"] = self.max
        dic["argmax"] = self.argmax
        dic["id"] = self.id
        dic["parents"] = self.parent_list
        return dic

    def __setstate__(self, state):
        self.__init__((state["size"], state["max"], state["argmax"]), iden=state["id"])
        self.benchmark_offset = np.array(state["Offset"])
        self.benchmark_frequency = np.array(state["Freq"])
        self.parent_list = state["parents"]
