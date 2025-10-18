from rag.app.contracts import validate_chunk_metadata


def test_chunk_contract_accepts_valid_record():
    record = {
        "source": "Registro Oficial",
        "title": "Ley Orgánica Reformatoria",
        "ro_number": "RO 563",
        "ro_date": "2023-10-15",
        "article": "Art. 72",
        "authority": "law",
        "vigency": "2025-10-10",
        "url": "https://www.registroficial.gob.ec/documentos/ro-563.pdf",
    }
    assert validate_chunk_metadata(record) == []


def test_chunk_contract_reports_missing_fields():
    record = {
        "source": "Registro Oficial",
        "title": "Ley",
        "article": "Art. 1",
        "authority": "memo",
        "vigency": "2025/10/10",
        "url": "registroficial.gob.ec",
    }
    errors = validate_chunk_metadata(record)
    assert any("missing keys" in error for error in errors)
    assert "authority" in " ".join(errors)
    assert "url is not absolute" in errors
    assert "ro_date must be" in " ".join(errors)
    assert "vigency must be" in " ".join(errors)