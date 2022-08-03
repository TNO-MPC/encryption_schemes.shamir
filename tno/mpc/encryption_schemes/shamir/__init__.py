"""
Shamir secret sharing scheme
"""

# Explicit re-export of all functionalities, such that they can be imported properly. Following
# https://www.python.org/dev/peps/pep-0484/#stub-files and
# https://mypy.readthedocs.io/en/stable/command_line.html#cmdoption-mypy-no-implicit-reexport
from .shamir import ShamirSecretSharingScheme as ShamirSecretSharingScheme
from .shamir import ShamirShares as ShamirShares
from .shamir_secret_sharing_integers import IntegerShares as IntegerShares
from .shamir_secret_sharing_integers import (
    ShamirSecretSharingIntegers as ShamirSecretSharingIntegers,
)

__version__ = "1.1.0"
