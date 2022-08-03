# TNO MPC Lab - Encryption Schemes - Shamir

The TNO MPC lab consists of generic software components, procedures, and functionalities developed and maintained on a regular basis to facilitate and aid in the development of MPC solutions. The lab is a cross-project initiative allowing us to integrate and reuse previously developed MPC functionalities to boost the development of new protocols and solutions.

The package tno.mpc.encryption_schemes.shamir is part of the TNO Python Toolbox.

*Limitations in (end-)use: the content of this software package may solely be used for applications that comply with international export control laws.*  
*This implementation of cryptographic software has not been audited. Use at your own risk.*

## Documentation

Documentation of the tno.mpc.encryption_schemes.shamir package can be found [here](https://docs.mpc.tno.nl/encryption_schemes/shamir/1.1.0).

## Install

Easily install the tno.mpc.encryption_schemes.shamir package using pip:
```console
$ python -m pip install tno.mpc.encryption_schemes.shamir
```

If you wish to run the tests you can use:
```console
$ python -m pip install 'tno.mpc.encryption_schemes.shamir[tests]'
```

### Note:
A significant performance improvement can be achieved by installing the GMPY2 library.
```console
$ python -m pip install 'tno.mpc.encryption_schemes.shamir[gmpy]'
```

## Usage

The shamir secret sharing module can be used as follows:

```python
from tno.mpc.encryption_schemes.shamir import ShamirSecretSharingScheme, ShamirShares

# Initialize a three-out-of-five secrect sharing scheme with prime 10657
# Note: the polynomial degree is one less than the number of parties needed for reconstruction
shamir_scheme = ShamirSecretSharingScheme(10657, 5, 2)
# Share a secret integer
sharing = shamir_scheme.share_secret(42)
# When receiving shares a reconstructor can be created as follows
reconstructor = ShamirShares(
    shamir_scheme, {1: sharing.shares[1], 2: sharing.shares[2], 3: sharing.shares[3]}
)
# Reconstruct the secret and check if it is the expected result
assert 42 == sharing.reconstruct_secret() == reconstructor.reconstruct_secret()
```

