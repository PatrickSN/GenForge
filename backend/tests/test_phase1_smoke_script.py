from __future__ import annotations

import pytest

from scripts.smoke_phase1 import SmokeFailure, normalize_base_url


def test_normalize_base_url_rejects_empty_value() -> None:
    with pytest.raises(SmokeFailure, match="empty"):
        normalize_base_url("")


def test_normalize_base_url_requires_scheme_and_host() -> None:
    with pytest.raises(SmokeFailure, match="scheme and host"):
        normalize_base_url("127.0.0.1:8000")


def test_normalize_base_url_removes_trailing_slash() -> None:
    assert normalize_base_url("http://127.0.0.1:8000/") == "http://127.0.0.1:8000"
