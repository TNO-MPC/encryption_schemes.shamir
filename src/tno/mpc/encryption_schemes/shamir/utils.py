"""
Useful functions for the shamir module.
"""

from __future__ import annotations

from functools import reduce


def mult_list(list_: list[int], modulus: int = 0) -> int:
    """
    Utility function to multiply a list of numbers in a modular group

    :param list_: list of elements
    :param modulus: modulus to be applied, use 0 for no modulus
    :return: product of the elements in the list modulo the modulus
    """
    if modulus:
        return reduce(lambda a, b: (a * b) % modulus, list_, 1)
    return reduce(lambda a, b: a * b, list_, 1)
