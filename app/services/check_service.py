from dataclasses import asdict

from sqlalchemy.orm import Session

from app.core.classifier import detect_document_type
from app.core.rules import DocumentInfo, check_completeness, compute_status, validate_file
from app.models.check import Check

STATUS_LABELS = {
    "approved": "Можно заявлять в банк",
    "rejected": "Нельзя заявлять в банк",
    "check_in_progress": "Проверка выполняется",
}


def run_check(db: Session, program: str, files: list[tuple[str, bytes]]) -> Check:
    documents = [
        DocumentInfo(name=name, detected_type=detect_document_type(name), size_bytes=len(content))
        for name, content in files
    ]

    issues = []
    for doc in documents:
        issues += validate_file(doc)
    issues += check_completeness(program, documents)

    status = compute_status(issues)
    reason = next((issue.message for issue in issues if issue.level == "error"), None)

    check = Check(
        program=program,
        status=status,
        reason=reason,
        issues=[asdict(issue) for issue in issues],
        documents=[
            {"name": doc.name, "detected_type": doc.detected_type, "size_kb": doc.size_bytes // 1024}
            for doc in documents
        ],
        extracted={}, #пустой словарь-заглушка, это зона ответственности будущего AI-модуля
    )
    db.add(check)
    db.commit()
    db.refresh(check)
    return check