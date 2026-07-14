from datetime import datetime
from typing import Literal
from zoneinfo import ZoneInfo

from pydantic import BaseModel, ConfigDict, field_serializer

# checked_at хранится в БД как UTC (datetime.utcnow() в models/check.py);
# наружу в API отдаём в московском времени для удобства
_MOSCOW_TZ = ZoneInfo("Europe/Moscow")


def _as_moscow_time(value: datetime) -> datetime:
    return value.replace(tzinfo=ZoneInfo("UTC")).astimezone(_MOSCOW_TZ)


class IssueSchema(BaseModel):
    level: Literal["error", "warning"]
    message: str


class DocumentSchema(BaseModel):
    name: str
    detected_type: str | None
    size_kb: int


class ExtractedSchema(BaseModel):
    contractor: str | None = None
    amount: str | None = None
    date: str | None = None
    subject: str | None = None


class CheckResult(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    check_id: str
    status: Literal["approved", "rejected", "check_in_progress"]
    status_label: str
    reason: str | None
    issues: list[IssueSchema]
    documents: list[DocumentSchema]
    extracted: ExtractedSchema
    checked_at: datetime

    @field_serializer("checked_at")
    def _serialize_checked_at(self, value: datetime) -> datetime:
        return _as_moscow_time(value)


class CheckListItem(BaseModel):
    id: str
    checked_at: datetime
    program: str
    status: str
    documents_count: int

    @field_serializer("checked_at")
    def _serialize_checked_at(self, value: datetime) -> datetime:
        return _as_moscow_time(value)

