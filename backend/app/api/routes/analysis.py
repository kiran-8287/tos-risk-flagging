import os
import uuid
import logging
from fastapi import APIRouter, UploadFile, File, HTTPException, Body
from pydantic import BaseModel
from typing import List, Optional

from app.services.document_parser import get_parser
from app.services.clause_segmenter import ClauseSegmenter
from app.services.predictor import Predictor
from app.services.risk_aggregator import RiskAggregator
from app.core.config import settings

logger = logging.getLogger(__name__)

router = APIRouter()
segmenter = ClauseSegmenter()
predictor = Predictor()
aggregator = RiskAggregator()


class ClauseResponse(BaseModel):
    id: str
    text: str
    label: str
    section: str | None = None
    startOffset: int
    endOffset: int


class AnalysisResponse(BaseModel):
    id: str
    filename: str
    totalClauses: int
    safeCount: int
    neutralCount: int
    riskyCount: int
    safePercentage: float
    neutralPercentage: float
    riskyPercentage: float
    overallAssessment: str
    clauses: List[ClauseResponse]
    riskyClauses: List[ClauseResponse]


class TextAnalysisRequest(BaseModel):
    text: str
    filename: Optional[str] = "pasted-text.txt"


class AnalyzeTextResponse(BaseModel):
    id: str
    filename: str
    totalClauses: int
    safeCount: int
    neutralCount: int
    riskyCount: int
    safePercentage: float
    neutralPercentage: float
    riskyPercentage: float
    overallAssessment: str
    clauses: List[ClauseResponse]
    riskyClauses: List[ClauseResponse]


def _run_analysis(text: str, filename: str) -> AnalysisResponse:
    if not text.strip():
        raise HTTPException(status_code=400, detail="Document contains no extractable text.")
    clauses = segmenter.segment(text)
    if not clauses:
        raise HTTPException(status_code=400, detail="No analyzable clauses found in the document.")
    clause_results = predictor.predict(clauses)
    summary = aggregator.aggregate(clause_results)
    return AnalysisResponse(
        id=str(uuid.uuid4()),
        filename=filename,
        totalClauses=summary["totalClauses"],
        safeCount=summary["safeCount"],
        neutralCount=summary["neutralCount"],
        riskyCount=summary["riskyCount"],
        safePercentage=summary["safePercentage"],
        neutralPercentage=summary["neutralPercentage"],
        riskyPercentage=summary["riskyPercentage"],
        overallAssessment=summary["overallAssessment"],
        clauses=[ClauseResponse(**c) for c in clause_results],
        riskyClauses=[ClauseResponse(**c) for c in clause_results if c["label"] == "Risky"],
    )


@router.post("/documents/analyze", response_model=AnalysisResponse)
async def analyze_document(file: UploadFile = File(...)):
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file provided.")
    ext = os.path.splitext(file.filename)[1].lower()
    allowed = {e.strip().lower() for e in settings.UPLOAD_ALLOWED_EXTENSIONS_STR.split(",")}
    if ext not in allowed:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type: {ext}. Allowed: {', '.join(sorted(allowed))}",
        )
    tmp_path = os.path.join("tmp", f"{uuid.uuid4()}{ext}")
    os.makedirs("tmp", exist_ok=True)
    try:
        content = await file.read()
        if len(content) > settings.UPLOAD_MAX_SIZE:
            raise HTTPException(status_code=400, detail="File exceeds maximum allowed size.")
        with open(tmp_path, "wb") as f:
            f.write(content)
        parser = get_parser(ext)
        text = parser.parse(tmp_path)
        return _run_analysis(text, file.filename)
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("Document analysis failed")
        raise HTTPException(status_code=500, detail="Document analysis failed.")
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)


@router.post("/documents/analyze-text", response_model=AnalyzeTextResponse)
async def analyze_text(request: TextAnalysisRequest):
    cleaned = request.text.replace("\r\n", "\n").replace("\r", "\n")
    result = _run_analysis(cleaned, request.filename or "pasted-text.txt")
    return AnalyzeTextResponse(**result.dict())
