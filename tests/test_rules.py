from app.core.rules import (
    DocumentInfo,
    Issue,
    check_completeness,
    compute_status,
    validate_file,
)


def _doc(name: str, doc_type: str | None, size_bytes: int = 1024) -> DocumentInfo:
    return DocumentInfo(name=name, detected_type=doc_type, size_bytes=size_bytes)


class TestCheckCompleteness:
    def test_federal_missing_specification(self) -> None:
        documents = [_doc("договор.pdf", "contract"), _doc("счет.pdf", "invoice"), _doc("акт.pdf", "act")]
        issues = check_completeness("federal", documents)
        assert any("спецификация" in issue.message for issue in issues)

    def test_regional_complete_package_has_no_issues(self) -> None:
        documents = [_doc("договор.pdf", "contract"), _doc("счет.pdf", "invoice"), _doc("акт.pdf", "act")]
        assert check_completeness("regional", documents) == []

    def test_federal_complete_package_has_no_issues(self) -> None:
        documents = [
            _doc("договор.pdf", "contract"),
            _doc("спецификация.pdf", "specification"),
            _doc("счет.pdf", "invoice"),
            _doc("акт.pdf", "act"),
        ]
        assert check_completeness("federal", documents) == []


class TestValidateFile:
    def test_rejects_disallowed_extension(self) -> None:
        issues = validate_file(_doc("архив.zip", "contract"))
        assert any(issue.level == "error" for issue in issues)

    def test_rejects_oversized_file(self) -> None:
        issues = validate_file(_doc("договор.pdf", "contract", size_bytes=21 * 1024 * 1024))
        assert any(issue.level == "error" for issue in issues)

    def test_warns_on_unrecognized_filename(self) -> None:
        issues = validate_file(_doc("scan_0041.jpg", None))
        assert issues == [Issue("warning", "Не удалось определить тип документа: «scan_0041.jpg»")]

    def test_accepts_valid_recognized_file(self) -> None:
        assert validate_file(_doc("договор.pdf", "contract")) == []


class TestComputeStatus:
    def test_rejected_when_any_error(self) -> None:
        issues = [Issue("error", "missing doc"), Issue("warning", "unclear name")]
        assert compute_status(issues) == "rejected"

    def test_approved_when_only_warnings_or_no_issues(self) -> None:
        assert compute_status([Issue("warning", "unclear name")]) == "approved"
        assert compute_status([]) == "approved"
