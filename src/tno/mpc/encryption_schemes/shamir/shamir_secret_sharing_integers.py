"""
Utility for Shamir secret sharing over the integers.
"""

from __future__ import annotations

import math
import secrets
from typing import Any, TypedDict

from tno.mpc.communication import SupportsSerialization
from tno.mpc.encryption_schemes.utils import mod_inv

from tno.mpc.encryption_schemes.shamir.utils import mult_list

# Check to see if the communication module is available
try:
    from tno.mpc.communication import RepetitionError, Serialization

    COMMUNICATION_INSTALLED = True
except ModuleNotFoundError:
    COMMUNICATION_INSTALLED = False


class ShamirSecretSharingIntegers(SupportsSerialization):
    """
    Class with Shamir Secret sharing functionality over the integers
    """

    def __init__(
        self,
        kappa: int = 40,
        max_int: int = 5,
        number_of_parties: int = 10,
        polynomial_degree: int = 4,
    ) -> None:
        """
        Initialize a secret sharing over the integers

        :param kappa: statistical security parameter
        :param max_int: Value that together with kappa and number_of_parties determines the
            interval from which polynomial coefficients are randomly sampled. In general,
            the Paillier modulus is used for max.
        :param number_of_parties: number of shares that need to be created for each sharing
        :param polynomial_degree: degree of polynomials used to share secrets
        """
        self.kappa = kappa
        self.max_int = max_int
        self.number_of_parties = number_of_parties
        self.polynomial_degree = polynomial_degree
        # Random polynomial coefficients are sampled uniformly at random from the interval [-A,A],
        # with A as follows:
        self.randomness_interval = (
            (math.factorial(number_of_parties) ** 2) * (2**kappa) * max_int
        )
        self._van_der_monde: list[list[int]] | None = None

    @property
    def van_der_monde(self) -> list[list[int]]:
        """
        Vandermonde matrix for evaluation of polynomials at points [1,..,n].
        This essentialy creates a matrix that precomputes i**j for all possible i**j that are
        needed for the evaluation of sharing polynomials. We now have that i**j = Vm[i][j].
        To evaluate a polynomial p(x) = a0 + a1 * x + ... + ad * x**d we can simply compute
        a0 * Vm[x][0] + a1 * Vm[x][1] + ... + ad * Vm[x][d].

        :return: A VanDerMonde matrix of dimpensions self.polynomial_degree + 1 x self.number_of_parties
        """
        if not self._van_der_monde:
            self._van_der_monde = [
                [pow(i + 1, j) for j in range(self.polynomial_degree + 1)]
                for i in range(self.number_of_parties)
            ]
        return self._van_der_monde

    def share_secret(self, secret: int) -> IntegerShares:
        """
        Function that creates shares of a value for each party

        :param secret: secret to be shared
        :return: sharing of the secret
        """
        # Sample random polynomial of degree polynomial_degree with constant coefficient
        n = self.randomness_interval
        secret_poly = [math.factorial(self.number_of_parties) * secret] + [
            secrets.randbelow(2 * n + 1) - n for _ in range(self.polynomial_degree)
        ]
        # Create an array of all the shares
        # Player IDs are equal to the points of evaluation.
        shares = {
            ind
            + 1: sum(
                [
                    self.van_der_monde[ind][i] * secret_poly[i]
                    for i in range(self.polynomial_degree + 1)
                ]
            )
            for ind in range(self.number_of_parties)
        }
        scaling = math.factorial(self.number_of_parties)
        sharing = IntegerShares(self, shares, self.polynomial_degree, scaling)
        return sharing

    def __eq__(self, other: object) -> bool:
        """
        Compare equality between this ShamirSecretSharingIntegers and the other object.

        :param other: Object to compare with.
        :return: Boolean stating (in)equality
        """
        if isinstance(other, ShamirSecretSharingIntegers):
            return (
                self.kappa == other.kappa
                and self.max_int == other.max_int
                and self.number_of_parties == other.number_of_parties
                and self.polynomial_degree == other.polynomial_degree
            )
        # else
        return False

    class SerializedShamirSecretSharingIntegers(TypedDict):
        """
        Class which contains the information of the shamir secret share from which deserialization is possible.
        """

        kappa: int
        number_of_parties: int
        polynomial_degree: int
        max_int: int

    def serialize(
        self, **_kwargs: Any
    ) -> ShamirSecretSharingIntegers.SerializedShamirSecretSharingIntegers:
        r"""
        Serialization function for the shamir secret sharing integers scheme, which will be passed to
        the communication module

        :param \**_kwargs: optional extra keyword arguments
        :return: Dictionary containing the serialization of this ShamirSecretSharingIntegers scheme.
        """
        return {
            "kappa": self.kappa,
            "number_of_parties": self.number_of_parties,
            "polynomial_degree": self.polynomial_degree,
            "max_int": self.max_int,
        }

    @staticmethod
    def deserialize(
        obj: ShamirSecretSharingIntegers.SerializedShamirSecretSharingIntegers,
        **_kwargs: Any,
    ) -> ShamirSecretSharingIntegers:
        r"""
        Deserialization function for the shamir secret sharing integers scheme, which will be passed to
        the communication module

        :param obj: serialization of a shamir secret sharing integers scheme.
        :param \**_kwargs: optional extra keyword arguments
        :return: Deserialized ShamirSecretSharingInteger scheme.
        """
        return ShamirSecretSharingIntegers(
            kappa=obj["kappa"],
            number_of_parties=obj["number_of_parties"],
            polynomial_degree=obj["polynomial_degree"],
            max_int=obj["max_int"],
        )


class IntegerShares(SupportsSerialization):
    """
    Class that keeps track of the shares for a certain value that is secret shared over the integers.
    """

    def __init__(
        self,
        shamir_sss: ShamirSecretSharingIntegers,
        shares: dict[int, int],
        degree: int,
        scaling: int,
    ) -> None:
        self.scheme = shamir_sss
        self.shares = shares
        # The degree of the polynomial used for sharing the secret, i.e.
        # at least degree+1 shares are required to reconstruct.
        self.degree = degree
        self.n = self.scheme.number_of_parties
        self.n_fac = math.factorial(self.n)
        self.scaling = scaling

    def reconstruct_secret(self, modulus: int = 0) -> int:
        """
        Function that uses the shares from other parties to reconstruct the secret

        :param modulus: the modulus to use
        :raise ValueError: In case not enough shares are present to reconstruct the secret.
        :return: original secret
        """
        if len(self.shares) < self.degree + 1:
            raise ValueError("Too little shares to reconstruct.")

        # We will use the first self.degree+1 shares to reconstruct. This can be any subset.
        # Hence, here the reconstruction set is implicitly defined.
        reconstruction_shares = {
            key: self.shares[key] for key in list(self.shares.keys())[: self.degree + 1]
        }

        # We precompute some values so that we can do the Lagrange interpolation.
        lagrange_interpol_enum = {
            i: mult_list([j for j in reconstruction_shares.keys() if i != j])
            for i in reconstruction_shares.keys()
        }
        lagrange_interpol_denom = {
            i: mult_list([(j - i) for j in reconstruction_shares.keys() if i != j])
            for i in reconstruction_shares.keys()
        }

        # modulus=0 is treated as standard reconstruction.
        # Otherwise, reconstruct modulo modulus
        if modulus == 0:
            partial_recon = [
                (lagrange_interpol_enum[i] * self.n_fac * reconstruction_shares[i])
                // lagrange_interpol_denom[i]
                for i in reconstruction_shares.keys()
            ]  # The fractions in this list are all integral.
            secret = sum(partial_recon) // (
                self.scaling * self.n_fac
            )  # The scaling factor is a divisor of the enumerator.
        else:
            if self.scaling % modulus == 0:
                raise ValueError("Scaling is not divisible mod modulus")
            partial_recon = [
                (
                    (
                        lagrange_interpol_enum[i]
                        * self.n_fac
                        * (reconstruction_shares[i] % modulus)
                    )
                    // lagrange_interpol_denom[i]
                )
                % modulus
                for i in reconstruction_shares.keys()
            ]  # The fractions in this list are all integral.
            secret = (
                sum(partial_recon) * int(mod_inv(self.scaling * self.n_fac, modulus))
            ) % modulus
        return secret

    def __add__(self, other: IntegerShares) -> IntegerShares:
        """
        Add the shares belonging to the two given IntegerShares values together.

        :param other: Shares to be added to these shares.
        :raise ValueError: In case a different secret sharing scheme was used.
        :return: New IntegerShares object where the shares have been added together.
        """
        if self.scheme != other.scheme:
            raise ValueError(
                "Different secret sharing schemes have been used, i.e. shares are incompatible."
            )

        if self.scaling != other.scaling:
            raise ValueError("Incompatible shares, different scaling factors.")

        shares = {i: (self.shares[i] + other.shares[i]) for i in self.shares.keys()}
        degree = max(self.degree, other.degree)
        scaling = self.scaling
        return IntegerShares(self.scheme, shares, degree, scaling)

    def __mul__(self, other: IntegerShares) -> IntegerShares:
        """
        Multiply the shares belonging to the two given IntegerShares values together. Only
        possible when both schemes are the same.

        :param other: Shares to be multiplied with these shares.
        :return: New IntegerShares object where the shares have been multiplied together.
        """
        if self.scheme != other.scheme:
            # If self is multiplied (from the right) by another object, we redirect to the __rmul__
            # method of that object. Only implemented when other is a shamir secret sharing. In
            # this case all shares are reduced modulo the Shamir modulus and a shamir sharing is
            # returned.
            return NotImplemented
        shares = {i: (self.shares[i] * other.shares[i]) for i in self.shares.keys()}
        degree = self.degree + other.degree
        scaling = self.scaling * other.scaling
        return IntegerShares(self.scheme, shares, degree, scaling)

    def __rmul__(self, other: Any) -> Any:
        """
        Multiply the shares belonging to this value with a given scalar integer or ShamirShares
        object.

        :param other: ShamirShares or scalar to be multiplied with these shares.
        :return: New IntegerShares object where the shares have been multiplied together.
        """
        if isinstance(other, int):
            # Scalar multiplication from the left by an integer
            shares = {i: (other * self.shares[i]) for i in self.shares.keys()}
            degree = self.degree
            scaling = self.scaling
            return IntegerShares(self.scheme, shares, degree, scaling)
        # Else, we redirect to the __rmul__ functionality of other.
        return self * other

    def __eq__(self, other: object) -> bool:
        """
        Compare equality between this IntegerShares and the other object.

        :param other: Object to compare with.
        :return: Boolean stating (in)equality
        """

        if not isinstance(other, IntegerShares):
            return False

        return (
            other.shares == self.shares
            and other.degree == self.degree
            and other.scheme == self.scheme
            and other.scaling == self.scaling
        )

    class SerializedIntegerShares(TypedDict):
        """
        Class which contains the information of the integer shares from which deserialization is possible.
        """

        scheme: ShamirSecretSharingIntegers.SerializedShamirSecretSharingIntegers
        shares: dict[int, int]
        degree: int
        scaling: int

    def serialize(self, **_kwargs: Any) -> IntegerShares.SerializedIntegerShares:
        r"""
        Serialization function for the integer shares and corresponding scheme, which will be passed to
        the communication module

        :param \**_kwargs: optional extra keyword arguments
        :return: Dictionary containing the serialization of this IntegerShare object.
        """
        return {
            "scheme": self.scheme.serialize(),
            "shares": self.shares,
            "degree": self.degree,
            "scaling": self.scaling,
        }

    @staticmethod
    def deserialize(
        obj: IntegerShares.SerializedIntegerShares,
        **_kwargs: Any,
    ) -> IntegerShares:
        r"""
        Deserialization function for the integer shares and corresponding scheme, which will be passed to
        the communication module

        :param obj: serialization of the integer shares.
        :param \**_kwargs: optional extra keyword arguments
        :return: Deserialized IntegerShares object.
        """
        return IntegerShares(
            shamir_sss=ShamirSecretSharingIntegers.deserialize(obj["scheme"]),
            shares=obj["shares"],
            degree=obj["degree"],
            scaling=obj["scaling"],
        )


if COMMUNICATION_INSTALLED:
    try:
        Serialization.register_class(ShamirSecretSharingIntegers)
        Serialization.register_class(IntegerShares)
    except RepetitionError:
        pass
