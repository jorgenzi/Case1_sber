import unicodedata
import pytest
from app.core.classifier import detect_document_type


@pytest.mark.parametrize(
    "filename,expected",
    [
        ("Договор_47.pdf", "contract"),
        ("contract_2025.docx", "contract"),
        ("Спецификация к договору.pdf", "specification"),
        ("счет_на_оплату.pdf", "invoice"),
        ("Счёт-фактура.jpg", "invoice"),
        ("Акт_выполненных_работ.pdf", "act"),
        ("УПД_15.pdf", "act"),
        ("scan_0041.jpg", None),
    ],
)
def test_detect_document_type(filename: str, expected: str | None) -> None:
    assert detect_document_type(filename) == expected


def test_detect_document_type_nfd_filename() -> None:
    nfd_filename = unicodedata.normalize("NFD", "счёт.pdf")
    assert detect_document_type(nfd_filename) == "invoice"