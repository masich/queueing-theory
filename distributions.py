import math
import random
from abc import ABCMeta, abstractmethod
from collections import Iterator
from functools import reduce
from math import exp, log
from operator import mul


class DistributionGenerator(Iterator, metaclass=ABCMeta):
    @abstractmethod
    def __next__(self) -> float:
        pass


class ErlangDistributionGenerator(DistributionGenerator):
    def __init__(self, alpha: int, beta: float):
        assert alpha > 0
        self._alpha, self._beta = alpha, beta
        self._coefficient = (-self._beta / self._alpha)

    def __next__(self) -> float:
        prod = reduce(mul, [random.random() for _ in range(0, self._alpha)])
        return self._coefficient * math.log(prod)


class ExponentialDistributionGenerator(DistributionGenerator):
    def __init__(self, scale):
        super().__init__()
        self._scale = scale

    def __next__(self) -> float:
        r = random.random()
        return - self._scale * math.log(r)


class HyperExponentialDistributionGenerator(DistributionGenerator):
    def __init__(self, a: float, b: float, p: float, q: float):
        assert 0 <= p <= 1 and 0 <= q <= 1
        self._a, self._b, self._p, self._q = a, b, p, q

    def __next__(self) -> float:
        num = random.random()
        a_num, b_num = self._a * num, self._b * num
        exp_b_num = exp(b_num)

        return (exp(a_num - b_num) * (self._p * exp_b_num) + self._q * exp_b_num - exp_b_num - self._q + 1) / (
                self._q * (exp(a_num) - 1))


class WeibullDurationGenerator(DistributionGenerator):
    def __init__(self, k: float, lamb: float):
        assert k > 0
        self._k, self._lambda = k, lamb

    def __next__(self) -> float:
        num = random.random()
        return self._lambda * ((-1 * log(1.00001 - num)) ** (-1 / self._k))
