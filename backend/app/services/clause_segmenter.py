import re
from typing import List, Dict, Optional
from dataclasses import dataclass


@dataclass
class Clause:
    clause_id: str
    text: str
    section: Optional[str]
    start_offset: int
    end_offset: int


class ClauseSegmenter:
    """Split document text at structural and sentence boundaries."""

    _numbered = re.compile(r"^\s*(?:\d+\.)+\s+")
    _bullet = re.compile(r"^\s*[-*•‣]\s+")
    # Common abbreviations and initials should not create sentence boundaries.
    _sentence_end = re.compile(r"(?<=[.!?])(?:[\"'’”\)\]]*)\s+(?=[\"'“‘(\[]*[A-Z0-9])")

    def segment(self, text: str, min_clause_length: int = 20) -> List[Clause]:
        if not text or not text.strip():
            return []

        clauses: List[Clause] = []
        section: Optional[str] = None
        offset = 0
        for line in text.splitlines(keepends=True):
            raw = line.rstrip("\r\n")
            stripped = raw.strip()
            line_start = offset
            offset += len(line)
            if not stripped:
                continue
            if self._is_heading(stripped):
                section = stripped
                continue

            content_start = line_start + len(raw) - len(raw.lstrip())
            content_end = line_start + len(raw.rstrip())
            content = text[content_start:content_end]
            # A list item is an individual unit. Strip only the list marker;
            # the returned text otherwise remains a direct slice of source.
            marker = self._numbered.match(content) or self._bullet.match(content)
            if marker:
                content_start += marker.end()
                content = text[content_start:content_end]

            # Sentence boundaries are within a paragraph, so a long single-line
            # ToS paragraph is analyzed sentence by sentence. Keep semicolon-
            # joined legal clauses intact.
            starts = [0]
            for match in self._sentence_end.finditer(content):
                boundary = match.end()
                starts.append(boundary)
            starts.append(len(content))
            spans = []
            for left, right in zip(starts, starts[1:]):
                a, b = left, right
                while a < b and content[a].isspace():
                    a += 1
                while b > a and content[b - 1].isspace():
                    b -= 1
                if a < b:
                    spans.append((a, b))

            # Merge very short sentence fragments with the next sentence (or
            # previous at the end), avoiding meaningless standalone samples.
            merged: List[tuple[int, int]] = []
            for a, b in spans:
                if merged and b - a < min_clause_length:
                    merged[-1] = (merged[-1][0], b)
                else:
                    merged.append((a, b))
            for a, b in merged:
                clause_text = content[a:b]
                if len(clause_text.strip()) < min_clause_length:
                    continue
                clauses.append(Clause(
                    clause_id=f"clause_{len(clauses) + 1}",
                    text=clause_text,
                    section=section,
                    start_offset=content_start + a,
                    end_offset=content_start + b,
                ))
        return clauses

    def _is_heading(self, line: str) -> bool:
        if line.startswith("#"):
            return True
        numbered_heading = self._numbered.match(line)
        if numbered_heading and not re.search(r"[.!?]", line):
            title = line[numbered_heading.end():]
            if len(title) < 80 and len(title.split()) <= 7:
                return True
        return line.isupper() and len(line) > 3 and len(line) < 120

    def to_json(self, clauses: List[Clause]) -> List[Dict]:
        return [{
            "clause_id": c.clause_id,
            "text": c.text,
            "section": c.section,
            "start_offset": c.start_offset,
            "end_offset": c.end_offset,
        } for c in clauses]
