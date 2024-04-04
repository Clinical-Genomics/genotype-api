"""Module for the endpoint service."""

from genotype_api.database.store import Store


class BaseService:
    def __init__(self, store: Store):
        self.store: Store = store
