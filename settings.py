from distributions import WeibullDurationGenerator, ErlangDistributionGenerator

SIMULATION_TIME = 2 * 1000
SERVERS_COUNT = 2
PROCESSING_DISTRIBUTION = WeibullDurationGenerator(k=4, lamb=50)
ARRIVAL_DISTRIBUTION = ErlangDistributionGenerator(alpha=2, beta=20)
