from fastapi import APIRouter, HTTPException
from app.schemas.redact import RedactRequest, RedactResponse
from fastapi import UploadFile, File, HTTPException
from app.services.file_extractors.csv_extractor import get_csv_columns
from fastapi import UploadFile, File, HTTPException, Form
from app.services.file_extractors.csv_extractor import extract_selected_columns_as_text
from app.services.file_extractors.pdf_extractor import extract_text_from_pdf
from app.services.file_extractors.docx_extractor import extract_text_from_docx
from app.utils.helpers import redaction_helper
import json

router = APIRouter()

@router.post("/redact", response_model=RedactResponse)
def redact_plain_text(request: RedactRequest):
    try:
        return redaction_helper(request.text)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Reduction failed: {str(e)}"
        )

@router.post("/api/pdf", response_model=RedactResponse)
async def redact_pdf_file(file: UploadFile = File(...)):
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported")

    file_bytes = await file.read()
    try:
        text = extract_text_from_pdf(file_bytes)
        return redaction_helper(text)

    except Exception as e:
        raise HTTPException(
            status_code = 500,
            detail = f"PDF Redaction Failed: {str(e)}"
        )


@router.post("/api/docx", response_model=RedactResponse)
async def redact_docx_file(file: UploadFile = File(...)):
    if not file.filename.endswith(".docx"):
        raise HTTPException(status_code=400, detail="Only DOCX files are supported")

    file_bytes = await file.read()
    try:
        text = extract_text_from_docx(file_bytes)
        return redaction_helper(text)

    except Exception as e:
        raise HTTPException(
            status_code = 500,
            detail = f"DOCX Redaction Failed: {str(e)}"
        )
    

@router.post("/api/csv/columns")
async def get_csv_column_names(file: UploadFile = File(...)):
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only CSV files are supported")

    file_bytes = await file.read()

    try:
        columns = get_csv_columns(file_bytes)
        return {"columns": columns}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/api/redact/csv", response_model=RedactResponse)
async def redact_csv_file(
    file: UploadFile = File(...),
    selected_columns: str = Form(...)
):
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only CSV files are supported")

    file_bytes = await file.read()

    try:
        try:
            columns = json.loads(selected_columns)
        except json.JSONDecodeError:
            columns = [col.strip() for col in selected_columns.split(",") if col.strip()]

        text = extract_selected_columns_as_text(file_bytes, columns)
        return redaction_helper(text)

    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail="CSV redaction failed")
