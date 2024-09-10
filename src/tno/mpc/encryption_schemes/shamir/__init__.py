"""
Root imports for the tno.mpc.encryption_schemes.shamir package.
"""

# Explicit re-export of all functionalities, such that they can be imported properly. Following
# https://www.python.org/dev/peps/pep-0484/#stub-files and
# https://mypy.readthedocs.io/en/stable/command_line.html#cmdoption-mypy-no-implicit-reexport
from tno.mpc.encryption_schemes.shamir.shamir import (
    ShamirSecretSharingScheme as ShamirSecretSharingScheme,
)
from tno.mpc.encryption_schemes.shamir.shamir import ShamirShares as ShamirShares
from tno.mpc.encryption_schemes.shamir.shamir_secret_sharing_integers import (
    IntegerShares as IntegerShares,
)
from tno.mpc.encryption_schemes.shamir.shamir_secret_sharing_integers import (
    ShamirSecretSharingIntegers as ShamirSecretSharingIntegers,
)

__version__ = "1.3.2"
