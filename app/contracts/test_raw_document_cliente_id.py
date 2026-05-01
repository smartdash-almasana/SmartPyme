import pytest

from app.contracts.evidence_contract import DocumentRecord, RawDocument


def test_raw_document_requires_cliente_id():
    with pytest.raises(ValueError):
        RawDocument(
            cliente_id="",
            raw_document_id="r1",
            job_id=None,
            plan_id=None,
            file_path="/tmp/x",
            filename="x.pdf",
            file_hash_sha256="abc",
        )


def test_document_record_requires_cliente_id():
    with pytest.raises(ValueError):
        DocumentRecord(
            cliente_id="",
            document_id="d1",
            raw_document_id="r1",
            job_id=None,
            plan_id=None,
            filename="x.pdf",
            parser="pdf",
            text_hash="abc",
        )


def test_valid_instantiation():
    doc = RawDocument(
        cliente_id="c1",
        raw_document_id="r1",
        job_id=None,
        plan_id=None,
        file_path="/tmp/x",
        filename="x.pdf",
        file_hash_sha256="abc",
    )
    rec = DocumentRecord(
        cliente_id="c1",
        document_id="d1",
        raw_document_id="r1",
        job_id=None,
        plan_id=None,
        filename="x.pdf",
        parser="pdf",
        text_hash="abc",
    )
    assert doc.cliente_id == "c1"
    assert rec.cliente_id == "c1"
