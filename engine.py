"""Core decisioning engine.

Equivalent to engine.hpp/cpp in the C++ version. Given reference data
(EngineData), evaluates individual return requests end to end:
return-window check -> risk scoring -> decision band.
"""

from typing import Dict, List, Optional

from returns.models import EngineData, ReturnRequest, ReturnDecision, PointBand, DecisionBand


class Engine:
    def __init__(self, data: EngineData):
        self._data = data
        # account_id -> list of every account in its linked group (including itself)
        self._linked_group_index: Dict[str, List[str]] = {}
        self._build_linked_group_index()

    def _build_linked_group_index(self) -> None:
        for group in self._data.account_links:
            for account_id in group.accounts:
                self._linked_group_index[account_id] = group.accounts

    def _return_window_for_category(self, category: str) -> int:
        for rule in self._data.category_rules:
            if rule.category == category:
                return rule.return_window_days
        for rule in self._data.category_rules:
            if rule.category == "DEFAULT":
                return rule.return_window_days
        return 30  # hard fallback if no rules configured at all

    def _total_return_history(self, account_id: str) -> int:
        members = self._linked_group_index.get(account_id, [account_id])
        total = 0
        for member in set(members):
            profile = self._data.account_profiles.get(member)
            if profile is not None:
                total += profile.return_count
        return total

    @staticmethod
    def _points_for_value(bands: List[PointBand], value) -> int:
        for band in bands:
            if band.min <= value <= band.max:
                return band.points
        return 0  # no matching band -> no points contributed

    def _band_for_score(self, score: int) -> Optional[DecisionBand]:
        for band in self._data.decision_bands:
            if band.min <= score <= band.max:
                return band
        return None

    def evaluate(self, request: ReturnRequest) -> ReturnDecision:
        # Step 1: hard gate on the category's return window.
        window = self._return_window_for_category(request.category)
        if request.days_since_purchase > window:
            return ReturnDecision(
                request_id=request.request_id,
                risk_score=None,
                decision="REJECT",
                reason="RETURN_WINDOW_EXPIRED",
            )

        # Step 2: risk scoring across three factors.
        history_total = self._total_return_history(request.account_id)
        history_points = self._points_for_value(self._data.scoring_rules.return_history_points, history_total)
        age_points = self._points_for_value(self._data.scoring_rules.account_age_points, request.account_age_days)
        value_points = self._points_for_value(
            self._data.scoring_rules.order_value_points, int(request.order_value_usd)
        )

        score = max(0, min(100, history_points + age_points + value_points))

        # Step 3: map score to decision band.
        band = self._band_for_score(score)
        if band is not None:
            reason = None if band.decision == "AUTO_APPROVE" else band.reason
            return ReturnDecision(
                request_id=request.request_id, risk_score=score, decision=band.decision, reason=reason
            )

        # No configured band covers this score -- default to manual review to be safe.
        return ReturnDecision(
            request_id=request.request_id,
            risk_score=score,
            decision="MANUAL_REVIEW",
            reason="UNSCORED_BAND",
        )
