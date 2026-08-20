"""App-level conftest for crushme_app tests.

Provides domain-specific fixtures (products, categories, etc.).
"""

import pytest

from .factories import create_product, create_user, create_woocommerce_product


@pytest.fixture
def user_factory(db):
    return create_user


@pytest.fixture
def product(db):
    """Active product with default values."""
    return create_product()


@pytest.fixture
def woocommerce_product_factory(db):
    return create_woocommerce_product
