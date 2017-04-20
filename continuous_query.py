"""
    Sample query for the continuous task jsons

"""

import library.continous as continuous
import library.costs as costs

# We can use the ContinuousGroup in place of the TestGroup for the cost stuff

trial = continuous.ContinousGroup("library/data/20170403_PM/Test 2017-04-03_15-45-39.json")
results = costs.compute_noise_cost(trial)

print(results)