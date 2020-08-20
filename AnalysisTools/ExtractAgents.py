import pickle
import numpy as np
from glob import glob
import re
import os


# Loading --------------------------------------------------------------------------------------------------------------

def load_agents_last_iteration(folder):
    ags = list()
    filenames = glob(f"{folder}/*.pickle")
    filenames = list(filter(lambda x: "Iteration" in x, filenames))
    filenames.sort(key=lambda k: int(re.sub('\D', '', k)))
    # assume we only have relevant files in the folder, take the last sorted .pickle file
    ea_path = filenames[-1]
    numbers = ''.join((ch if ch in '0123456789' else ' ') for ch in ea_path)
    resume_from = int(numbers.split()[-1])
    with open(f"{ea_path}", "rb") as f:
        resume = pickle.load(f)
    print(f"Execution successfully loaded from {folder} .")
    if len(resume) == 3:
        loc = input("Use local populations ? (y/n)")
        loc = loc.lower()
        while loc != "y" and loc != "n":
            loc = input("Use local populations ? (y/n)")
            loc = loc.lower()

        if loc:
            for pop_ag in resume[0]:
                for ag in pop_ag[(3*len(pop_ag))//4:]:
                    ags.append(ag)
        else:
            for ag in resume[2][(3*len(resume[2]))//4:]:
                ags.append(ag)
    elif len(resume) == 2:
        ags = resume[0]
    else:
        for ea_pair in resume:
            E, theta = ea_pair
            ags.append(theta)
    return ags

