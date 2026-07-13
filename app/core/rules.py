from dataclasses import dataclass
from typing import Literal

from app.core.config import settings

Level = Literal["error", "warning"]
Program = Literal["federal", "regional"]
Status = Literal["approved", "rejected", "check_in_progress"]

REQUIRED_DOCUMENTS: dict[Program, set[str]] = {
    "federal": {"contract", "specification", "invoice", "act"},
    "regional": {"contract", "invoice", "act"},
}

DOCUMENT_LABELS = {
    "contract": "договор",
    "specification": "спецификация",
    "invoice": "счёт",
    "act": "акт/УПД",
}

ALLOWED_EXTENSIONS = {"pdf", "docx", "jpg", "jpeg", "png"}
MAX_FILE_SIZE_BYTES = settings.max_file_size_mb * 1024 * 1024


@dataclass(frozen=True)
class Issue:
    level: Level
    message: str


@dataclass
class DocumentInfo:
    name: str
    detected_type: str | None
    size_bytes: int


def validate_file(doc: DocumentInfo) -> list[Issue]:
    issues: list[Issue] = []
    extension = doc.name.rsplit(".", 1)[-1].lower() if "." in doc.name else ""

    if extension not in ALLOWED_EXTENSIONS:
        issues.append(Issue("error", f"Недопустимый формат файла: «{doc.name}»"))

    if doc.size_bytes > MAX_FILE_SIZE_BYTES:
        issues.append(Issue("error", f"Файл превышает {settings.max_file_size_mb} МБ: «{doc.name}»"))
    
    if doc.detected_type is None:
        issues.append(Issue("warning", f"Не удалось определить тип документа: «{doc.name}»"))

    return issues


def check_completeness(program: Program, documents: list[DocumentInfo]) -> list[Issue]:
    present_types = {doc.detected_type for doc in documents if doc.detected_type}
    missing = REQUIRED_DOCUMENTS[program] - present_types
    return [
        Issue("error", f"Отсутствует обязательный документ: {DOCUMENT_LABELS[doc_type]}")
        for doc_type in sorted(missing)
    ]


def compute_status(issues: list[Issue]) -> Status:
    if any(issue.level == "error" for issue in issues):
        return "rejected"
    return "approved"