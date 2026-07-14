from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.models.check import Check
from app.models.database import get_db
from app.schemas.check import CheckListItem, CheckResult, DocumentSchema, ExtractedSchema, IssueSchema
from app.services.check_service import STATUS_LABELS, run_check

router = APIRouter(prefix="/api/checks", tags=["checks"])


def _to_result(check: Check) -> CheckResult:
    return CheckResult(
        check_id=check.id,
        status=check.status,
        status_label=STATUS_LABELS[check.status],
        reason=check.reason,
        issues=[IssueSchema(**issue) for issue in check.issues],
        documents=[DocumentSchema(**doc) for doc in check.documents],
        extracted=ExtractedSchema(**check.extracted),
        checked_at=check.checked_at,
    )


@router.post("", response_model=CheckResult, status_code=201)
async def create_check(
    program: str = Form(...),
    files: list[UploadFile] = File(...),
    db: Session = Depends(get_db),
) -> CheckResult:
    if program not in ("federal", "regional"):
        raise HTTPException(status_code=422, detail="program должна быть 'federal' или 'regional'")
    if not files:
        raise HTTPException(status_code=400, detail="Нужно передать хотя бы один файл")
    
    loaded = [(f.filename or "unnamed", await f.read()) for f in files]
    check = run_check(db, program, loaded)
    return _to_result(check)


@router.get("", response_model=list[CheckListItem])
def list_checks(db: Session = Depends(get_db)) -> list[CheckListItem]:
    checks = db.query(Check).order_by(Check.checked_at.desc()).all()
    return [
        CheckListItem(
            id=check.id,
            checked_at=check.checked_at,
            program=check.program,
            status=check.status,
            documents_count=len(check.documents),
        )
        for check in checks
    ]


@router.get("/{check_id}", response_model=CheckResult)
def get_check(check_id: str, db: Session = Depends(get_db)) -> CheckResult:
    check = db.get(Check, check_id)
    if check is None:
        raise HTTPException(status_code=404, detail="Проверка не найдена")
    return _to_result(check)