"""Configurazione pytest condivisa."""

from __future__ import annotations

import pytest


@pytest.fixture
def base_url_coll() -> str:
    return "https://api-coll.museiitaliani.it"
