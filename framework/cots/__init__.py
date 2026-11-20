"""Built-in COTS catalog, classified by Python EPS component inheritance."""

from .catalog import Catalog, CatalogBinding, CatalogFact, CatalogProduct, load_catalog


def get_product(product_id, **options):
    """Construct a detached fixed product with explicit role and fact selections."""
    return load_catalog().product(product_id, **options)


__all__ = ["Catalog", "CatalogBinding", "CatalogFact", "CatalogProduct", "load_catalog", "get_product"]
