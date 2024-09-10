# TNO PET Lab - secure Multi-Party Computation (MPC) - Encryption Schemes - Shamir

Implementation of the Shamir Secret Sharing scheme. 

### PET Lab

The TNO PET Lab consists of generic software components, procedures, and functionalities developed and maintained on a regular basis to facilitate and aid in the development of PET solutions. The lab is a cross-project initiative allowing us to integrate and reuse previously developed PET functionalities to boost the development of new protocols and solutions.

The package `tno.mpc.encryption_schemes.shamir` is part of the [TNO Python Toolbox](https://github.com/TNO-PET).

_Limitations in (end-)use: the content of this software package may solely be used for applications that comply with international export control laws._  
_This implementation of cryptographic software has not been audited. Use at your own risk._

## Documentation

Documentation of the `tno.mpc.encryption_schemes.shamir` package can be found
[here](https://docs.pet.tno.nl/mpc/encryption_schemes/shamir/1.3.2).

## Install

Easily install the `tno.mpc.encryption_schemes.shamir` package using `pip`:

```console
$ python -m pip install tno.mpc.encryption_schemes.shamir
```

_Note:_ If you are cloning the repository and wish to edit the source code, be
sure to install the package in editable mode:

```console
$ python -m pip install -e 'tno.mpc.encryption_schemes.shamir'
```

If you wish to run the tests you can use:

```console
$ python -m pip install 'tno.mpc.encryption_schemes.shamir[tests]'
```
_Note:_ A significant performance improvement can be achieved by installing the GMPY2 library.

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
For the performance it is important to bear in mind the following information:
Both `ShamirSecretSharingScheme` and `ShamirSecretSharingIntegers` make use of a VanderMonde matrix when sharing a secret. The size of this matrix grows exponentially with the number of parties. This matrix is constructed on-the-fly, which means that the first time the property `van_der_monde` is called, this matrix is constructed. This generally happens during the `secret_share` operation. If you would like to initialize this in an earlier stage, you can put the following piece of code wherever you want the initialization to take place:
````python
# scheme is initialized
scheme = ShamirSecretSharingScheme(...)

# VanderMonde matrix is initialized
_ = scheme.van_der_monde
````

