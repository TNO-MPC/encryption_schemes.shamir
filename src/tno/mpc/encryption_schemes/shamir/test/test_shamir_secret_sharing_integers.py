"""
Tests for the regular Shamir Secret Sharing scheme functionality.
"""

from __future__ import annotations

import pytest
import sympy
from _pytest.fixtures import SubRequest

from tno.mpc.encryption_schemes.shamir import IntegerShares, ShamirSecretSharingIntegers

moduli = [sympy.prime(_) for _ in range(13000, 13010)]  # at least 10657
polynomial_degrees = [2, 2, 2, 3, 3, 3, 4, 4, 5, 5]
n_parties = [5, 6, 7, 8, 9, 10, 11, 12, 13, 14]
secrets = list(range(0, 100, 10))
kappas = [40, 40, 40, 40, 40, 80, 80, 80, 80, 80]
max_ints = [1000 + _ for _ in range(10)]


@pytest.fixture(
    name="shamir_scheme",
    params=[
        {"number_of_parties": n_parties[_], "polynomial_degree": polynomial_degrees[_]}
        for _ in range(10)
    ],
)
def fixture_shamir_scheme(request: SubRequest) -> ShamirSecretSharingIntegers:
    """
    Create Shamir Schemes using the parameters defined in the pre-amble.

    :param request: Request for a scheme.
    :return: ShamirSecretSharingIntegers scheme using one of the parameter sets.
    """
    return ShamirSecretSharingIntegers(max_int=1000, **request.param)


@pytest.mark.parametrize(
    "scheme_parameters",
    [(kappas[_], max_ints[_], n_parties[_], polynomial_degrees[_]) for _ in range(10)],
)
def test_integer_shamir_scheme_equality(
    scheme_parameters: tuple[int, int, int, int]
) -> None:
    """
    Test whether two equal Integer Shamir schemes are seen as equal.

    :param scheme_parameters: A Tuple containing modulus, number of parties and a polynomial degree. Used to
        instantiate the scheme.
    """
    assert ShamirSecretSharingIntegers(
        *scheme_parameters
    ) == ShamirSecretSharingIntegers(*scheme_parameters)


@pytest.mark.parametrize(
    "scheme_parameters",
    [(kappas[_], max_ints[_], n_parties[_], polynomial_degrees[_]) for _ in range(10)],
)
def test_integer_shamir_scheme_inequality(
    scheme_parameters: tuple[int, int, int, int]
) -> None:
    """
    Test whether two different Integer Shamir schemes are seen as not equal.

    Also tests whether Integer Shamir scheme unequal to other object.

    :param scheme_parameters: A Tuple containing modulus, number of parties and a polynomial degree. Used to
        instantiate the scheme.
    """
    kappa, max_int, n_party, polynomial_degree = scheme_parameters
    correct_scheme = ShamirSecretSharingIntegers(
        kappa, max_int, n_party, polynomial_degree
    )
    assert correct_scheme != ShamirSecretSharingIntegers(
        kappa + 1, max_int, n_party, polynomial_degree
    )
    assert correct_scheme != ShamirSecretSharingIntegers(
        kappa, max_int + 1, n_party, polynomial_degree
    )
    assert correct_scheme != ShamirSecretSharingIntegers(
        kappa, max_int, n_party + 1, polynomial_degree
    )
    assert correct_scheme != ShamirSecretSharingIntegers(
        kappa, max_int, n_party, polynomial_degree + 1
    )
    # test non-scheme comparison
    assert correct_scheme != scheme_parameters


@pytest.mark.parametrize("secret", secrets)
def test_share_and_reconstruct_secret(
    shamir_scheme: ShamirSecretSharingIntegers, secret: int
) -> None:
    """
    Test the sharing and reconstructing of a secret using a shamir sharing scheme.

    :param shamir_scheme: Shamir sharing scheme to be used.
    :param secret: Secret to be shared and reconstructed.
    """
    sharing = shamir_scheme.share_secret(secret)
    assert sharing.reconstruct_secret() == secret


@pytest.mark.parametrize(
    "secret_1, secret_2",
    [(secrets[i], secrets[j]) for i in range(10) for j in range(10)],
)
def test_add(
    shamir_scheme: ShamirSecretSharingIntegers, secret_1: int, secret_2: int
) -> None:
    """
    Test the correct addition of two shared values using a shamir sharing scheme.

    :param shamir_scheme: The scheme with which both secrets are shared.
    :param secret_1: To be shared number.
    :param secret_2: To be shared number.
    """
    sharing_1 = shamir_scheme.share_secret(secret_1)
    sharing_2 = shamir_scheme.share_secret(secret_2)
    add_1 = sharing_1 + sharing_2
    add_2 = sharing_1 + sharing_2
    assert (
        secret_1 + secret_2 == add_1.reconstruct_secret() == add_2.reconstruct_secret()
    )


@pytest.mark.parametrize(
    "secret_1, secret_2",
    [(secrets[i], secrets[j]) for i in range(10) for j in range(10)],
)
def test_mul(
    shamir_scheme: ShamirSecretSharingIntegers, secret_1: int, secret_2: int
) -> None:
    """
    Test the correct multiplication of two shared values using a shamir sharing scheme.

    :param shamir_scheme: The scheme with which both secrets are shared.
    :param secret_1: To be shared number.
    :param secret_2: To be shared number.
    """
    sharing_1 = shamir_scheme.share_secret(secret_1)
    sharing_2 = shamir_scheme.share_secret(secret_2)
    mul_1 = sharing_1 * sharing_2
    mul_2 = sharing_1 * sharing_2
    assert (
        secret_1 * secret_2 == mul_1.reconstruct_secret() == mul_2.reconstruct_secret()
    )


@pytest.mark.parametrize(
    "secret_1, secret_2",
    [(secrets[i], secrets[j]) for i in range(10) for j in range(10)],
)
def test_rmul_scalar(
    shamir_scheme: ShamirSecretSharingIntegers, secret_1: int, secret_2: int
) -> None:
    """
    Test the correct multiplication of a scalar with a shared value.

    :param shamir_scheme: The scheme with which the secret is shared.
    :param secret_1: To be shared number.
    :param secret_2: Scalar for multiplication.
    """
    sharing_1 = shamir_scheme.share_secret(secret_1)
    mul = secret_2 * sharing_1
    assert secret_1 * secret_2 == mul.reconstruct_secret()


@pytest.mark.parametrize("secret", secrets)
def test_integer_shares_serialize_and_deserialize(
    shamir_scheme: ShamirSecretSharingIntegers, secret: int
) -> None:
    """
    Test the serializing the shamir secret sharing scheme

    :param shamir_scheme: Shamir sharing scheme to be used.
    :param secret: Secret to be shared and reconstructed.
    """
    sharing = shamir_scheme.share_secret(secret)
    serialized_shares = sharing.serialize()
    reconstructed_shares = IntegerShares.deserialize(serialized_shares)
    assert sharing == reconstructed_shares
    assert sharing.reconstruct_secret() == secret


@pytest.mark.parametrize(
    "scheme_parameters",
    [(kappas[_], max_ints[_], n_parties[_], polynomial_degrees[_]) for _ in range(10)],
)
@pytest.mark.parametrize("secret", secrets)
def test_integer_shares_equality(
    scheme_parameters: tuple[int, int, int, int], secret: int
) -> None:
    """
    Test whether two equal Integer shares are seen as equal.

    :param scheme_parameters: A Tuple containing modulus, number of parties and a polynomial degree. Used to
        instantiate the scheme.
    :param secret: A secret to share.
    """
    shares = ShamirSecretSharingIntegers(*scheme_parameters).share_secret(secret)
    shares2 = IntegerShares(shares.scheme, shares.shares, shares.degree, shares.scaling)
    assert shares == shares2


@pytest.mark.parametrize(
    "scheme_parameters",
    [(kappas[_], max_ints[_], n_parties[_], polynomial_degrees[_]) for _ in range(10)],
)
@pytest.mark.parametrize("secret", secrets)
def test_integer_shares_inequality(
    scheme_parameters: tuple[int, int, int, int], secret: int
) -> None:
    """
    Test whether two different Integer Shamir schemes are seen as not equal.

    Also tests whether Integer Shamir scheme unequal to other object.

    :param scheme_parameters: A Tuple containing modulus, number of parties and a polynomial degree. Used to
        instantiate the scheme.
    :param secret: A secret to share.
    """
    kappa, max_int, n_party, polynomial_degree = scheme_parameters
    correct_scheme = ShamirSecretSharingIntegers(
        kappa, max_int, n_party, polynomial_degree
    )
    shares = correct_scheme.share_secret(secret)

    # test different values
    assert shares != IntegerShares(
        shares.scheme, shares.shares, shares.degree + 1, shares.scaling
    )

    assert shares != IntegerShares(
        shares.scheme, shares.shares, shares.degree, shares.scaling + 1
    )
    shares_dict = shares.shares.copy()
    shares_dict[1] = shares_dict[1] - 1
    assert shares != IntegerShares(
        shares.scheme, shares_dict, shares.degree, shares.scaling
    )

    # test non-scheme comparison
    assert shares != scheme_parameters
