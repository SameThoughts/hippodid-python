"""Tests for batch character creation."""

import httpx

from tests.conftest import BATCH_JOB_JSON


JID = "j4000000-0000-0000-0000-000000000001"
TID = "t3000000-0000-0000-0000-000000000001"


def test_get_batch_job_status(client, mock_api):
    mock_api.get(f"/v1/jobs/{JID}").mock(return_value=httpx.Response(200, json=BATCH_JOB_JSON))
    job = client.get_batch_job_status(JID)
    assert job.status == "COMPLETED"
    assert job.progress.total == 10
    assert job.progress.succeeded == 10
    assert job.progress.failed == 0


def test_rows_to_csv():
    from hippodid.client import HippoDid

    rows = [
        {"name": "Alice", "role": "Engineer"},
        {"name": "Bob", "role": "Manager"},
    ]
    csv_bytes = HippoDid._rows_to_csv(rows)
    lines = csv_bytes.decode("utf-8").strip().splitlines()
    assert lines[0].strip() == "name,role"
    assert lines[1].strip() == "Alice,Engineer"
    assert lines[2].strip() == "Bob,Manager"


def test_rows_to_csv_empty():
    from hippodid.client import HippoDid

    assert HippoDid._rows_to_csv([]) == b""


def test_batch_create_validates_data_type(client):
    import pytest

    with pytest.raises(TypeError, match="list of dicts"):
        client.batch_create_characters(TID, "not-a-list", "id_col")


def test_batch_job_error_fields():
    """BatchJobError must map rowIndex, externalId, message from backend."""
    from hippodid.models import BatchJob

    job_with_errors = {
        **BATCH_JOB_JSON,
        "errors": [
            {"rowIndex": 3, "externalId": "SF-004", "message": "Duplicate external ID"},
            {"rowIndex": 7, "externalId": "SF-008", "message": "Missing name field"},
        ],
    }
    job = BatchJob.model_validate(job_with_errors)
    assert len(job.errors) == 2
    assert job.errors[0].row_index == 3
    assert job.errors[0].external_id == "SF-004"
    assert job.errors[0].message == "Duplicate external ID"
    assert job.errors[1].row_index == 7
    assert job.errors[1].external_id == "SF-008"


def test_upload_batch_sends_single_request(client, mock_api):
    """_upload_batch must send exactly one multipart request, not two."""
    route = mock_api.post("/v1/characters/batch").mock(
        return_value=httpx.Response(202, json=BATCH_JOB_JSON)
    )
    rows = [{"name": "Alice", "crm_id": "SF-001"}]
    job = client.batch_create_characters(TID, rows, "crm_id")
    assert job.job_id == JID
    assert route.call_count == 1
