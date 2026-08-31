import ipaddress
from pathlib import Path

import pytest
from fastapi import HTTPException

from app.core.ids import artifact_dir, require_investigation_id
from app.evidence_pipeline.retrieval.safety import UnsafeUrlError, assert_public_http_url, is_blocked_ip


def test_require_investigation_id_accepts_generated_ids() -> None:
    assert require_investigation_id("inv_abc123def456") == "inv_abc123def456"
    assert require_investigation_id("test-investigation") == "test-investigation"


def test_require_investigation_id_rejects_path_escape() -> None:
    with pytest.raises(HTTPException) as exc:
        require_investigation_id("../etc")
    assert exc.value.status_code == 400


def test_artifact_dir_stays_under_root(tmp_path: Path) -> None:
    path = artifact_dir(tmp_path, "inv_abc123def456")
    assert path.parent == tmp_path.resolve()


def test_private_literals_are_blocked() -> None:
    assert is_blocked_ip(ipaddress.ip_address("127.0.0.1"))
    assert is_blocked_ip(ipaddress.ip_address("10.0.0.8"))
    assert is_blocked_ip(ipaddress.ip_address("169.254.169.254"))
    with pytest.raises(UnsafeUrlError):
        assert_public_http_url("http://127.0.0.1/secret")
    with pytest.raises(UnsafeUrlError):
        assert_public_http_url("file:///etc/passwd")
