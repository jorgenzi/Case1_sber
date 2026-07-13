import re
import unicodedata

_TOKEN_SPLIT = re.compile(r"[^a-zA-Zа-яА-ЯёЁ0-9]+")

DOCUMENT_KEYWORDS: dict[str, tuple[str, ...]] = {
    "specification": ("специфик", "spec"),
    "act": ("акт", "упд", "act", "upd"),
    "invoice": ("счет", "счёт", "invoice", "schet"),
    "contract": ("договор", "contract", "dogovor"),
}

def detect_document_type(filename: str) -> str | None:
    filename = unicodedata.normalize("NFC", filename)
    stem = filename.rsplit(".", 1)[0] if "." in filename else filename
    tokens = [token.lower() for token in _TOKEN_SPLIT.split(stem) if token]

    for doc_type, keywords in DOCUMENT_KEYWORDS.items():
        if any(token.startswith(keyword) for token in tokens for keyword in keywords):
            return doc_type
    return None
