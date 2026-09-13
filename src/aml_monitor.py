"""Anti-money-laundering monitoring: structuring, velocity, and geo-risk."""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field
from typing import Any

import pandas as pd

from settings import get_section


@dataclass
class AmlAlert:
    customer_id: str
    alert_score: float
    severity: str
    typologies: list[str] = field(default_factory=list)
    evidence: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "customer_id": self.customer_id,
            "alert_score": round(self.alert_score, 2),
            "severity": self.severity,
            "typologies": self.typologies,
            "evidence": self.evidence,
        }


class AmlMonitor:
    """Score a customer's recent ledger for PMLA-style red flags."""

    def evaluate_customer(self, transactions: list[dict[str, Any]], customer_id: str) -> AmlAlert:
        cfg = get_section("aml")
        if not transactions:
            return AmlAlert(customer_id, 0.0, "clear", [], ["No recent transactions supplied."])

        frame = pd.DataFrame(transactions)
        score = 0.0
        typologies: list[str] = []
        evidence: list[str] = []

        near = frame[frame["amount"] >= 0.85 * cfg["structuring_threshold"]]
        near = near[near["amount"] < cfg["structuring_threshold"]]
        if len(near) >= cfg["structuring_window_count"]:
            score += 40
            typologies.append("structuring")
            evidence.append(
                f"{len(near)} credits/debits sit just below the Rs.{cfg['structuring_threshold']:,} CTR band."
            )

        if frame["amount"].sum() >= 2_000_000 and frame["counterparty_country"].nunique() >= 3:
            score += 20
            typologies.append("layering")
            evidence.append("Large value moved across three or more counterpart geographies.")

        high_risk = frame[frame["counterparty_country"].isin(cfg["high_risk_countries"])]
        if not high_risk.empty:
            score += 25
            typologies.append("high_risk_geography")
            evidence.append(
                "Activity involving "
                + ", ".join(sorted(high_risk["counterparty_country"].unique()))
            )

        if "hours_since_inflow" in frame.columns:
            rapid = frame[(frame["direction"] == "out") & (frame["hours_since_inflow"] <= cfg["rapid_turnover_hours"])]
            if len(rapid) >= 2:
                score += 20
                typologies.append("rapid_in_out")
                evidence.append("Funds leave the account within hours of incoming credits.")

        cash_share = float((frame["channel"] == "cash").mean()) if "channel" in frame.columns else 0.0
        if cash_share >= 0.45:
            score += 15
            typologies.append("cash_intensive")
            evidence.append(f"Cash channels account for {cash_share:.0%} of recent activity.")

        score = min(100.0, score)
        if score >= cfg["alert_score"] + 15:
            severity = "high"
        elif score >= cfg["alert_score"]:
            severity = "medium"
        elif score >= 25:
            severity = "watch"
        else:
            severity = "clear"

        if not evidence:
            evidence = ["No typology matched. Activity is within expected corridors."]

        return AmlAlert(customer_id, score, severity, typologies, evidence)

    def evaluate_batch(self, frame: pd.DataFrame) -> list[AmlAlert]:
        alerts: list[AmlAlert] = []
        for customer_id, group in frame.groupby("customer_id"):
            alerts.append(self.evaluate_customer(group.to_dict(orient="records"), str(customer_id)))
        return sorted(alerts, key=lambda item: item.alert_score, reverse=True)

    def summary(self, alerts: list[AmlAlert]) -> dict[str, int]:
        counts: dict[str, int] = defaultdict(int)
        for alert in alerts:
            counts[alert.severity] += 1
        return dict(counts)
