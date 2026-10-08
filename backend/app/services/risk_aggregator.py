from typing import List, Dict


class RiskAggregator:
    def aggregate(self, clauses: List[Dict]) -> Dict:
        total = len(clauses)
        safe_count = sum(1 for c in clauses if c["label"] == "Safe")
        neutral_count = sum(1 for c in clauses if c["label"] == "Neutral")
        risky_count = sum(1 for c in clauses if c["label"] == "Risky")

        safe_pct = (safe_count / total * 100) if total > 0 else 0.0
        neutral_pct = (neutral_count / total * 100) if total > 0 else 0.0
        risky_pct = (risky_count / total * 100) if total > 0 else 0.0

        if total == 0:
            overall = "No analyzable clauses found."
        elif risky_pct == 0:
            overall = (
                "No risky clauses were detected in this document. "
                "This does not guarantee the document is risk-free."
            )
        elif risky_pct <= 15:
            overall = (
                "A small portion of clauses were flagged as risky. "
                "Review the highlighted clauses for details."
            )
        elif risky_pct <= 40:
            overall = (
                "A moderate number of clauses were flagged as risky. "
                "Consider reviewing these clauses carefully."
            )
        else:
            overall = (
                "A large portion of clauses were flagged as risky. "
                "Exercise caution and seek professional advice if needed."
            )

        return {
            "totalClauses": total,
            "safeCount": safe_count,
            "neutralCount": neutral_count,
            "riskyCount": risky_count,
            "safePercentage": round(safe_pct, 2),
            "neutralPercentage": round(neutral_pct, 2),
            "riskyPercentage": round(risky_pct, 2),
            "overallAssessment": overall,
        }
