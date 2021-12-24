"""
Testing module of the tno.mpc.encryption_schemes.shamir library
"""

# Explicit re-export of all functionalities, such that they can be imported properly. Following
# https://www.python.org/dev/peps/pep-0484/#stub-files and
# https://mypy.readthedocs.io/en/stable/command_line.html#cmdoption-mypy-no-implicit-reexport
from tno.mpc.encryption_schemes.shamir.test.test_shamir_secret_sharing import (
    fixture_shamir_scheme as fixture_shamir_scheme,
)
