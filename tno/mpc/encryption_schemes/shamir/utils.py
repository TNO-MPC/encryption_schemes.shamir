"""
Useful functions for the shamir module.
"""

from functools import reduce
from typing import List


def mult_list(list_: List[int], modulus: int = 0) -> int:
    """
    Utility function to multiply a list of numbers in a modular group

    :param list_: list of elements
    :param modulus: modulus to be applied, use 0 for no modulus
    :return: product of the elements in the list modulo the modulus
    """
    if modulus:
        return reduce(lambda a, b: (a * b) % modulus, list_, 1)
    return reduce(lambda a, b: a * b, list_, 1)
