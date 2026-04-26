"""App-level conftest for crushme_app tests.

Provides domain-specific fixtures (products, categories, etc.).
"""

import pytest


@pytest.fixture
def product(db):
    """Active product with default values."""
    from crushme_app.models import Product
    return Product.objects.create(
        name_en='Test Product',
        name_es='Producto de Prueba',
        price='29.99',
        stock=10,
        is_active=True,
    )
