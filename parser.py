

import json
from typing import Dict, List

from returns.models import (
    CategoryRule,
    PointBand,
    ScoringRules,
    DecisionBand,
    AccountProfile,
    AccountLinkGroup,
    ReturnRequest,
    ReturnDecision,
)
from returns.file_io import read_file, read_lines


def parse_category_rules(path: str) -> List[CategoryRule]:
    data = json.loads(read_file(path))
    return [
        CategoryRule(category=item["category"], return_window_days=item["return_window_days"])
        for item in data["categories"]
    ]


def _parse_band_array(arr) -> List[PointBand]:
    return [PointBand(min=item["min"], max=item["max"], points=item["points"]) for item in arr]


def parse_scoring_rules(path: str) -> ScoringRules:
    data = json.loads(read_file(path))
    return ScoringRules(
        return_history_points=_parse_band_array(data["return_history_points"]),
        account_age_points=_parse_band_array(data["account_age_points"]),
        order_value_points=_parse_band_array(data["order_value_points"]),
    )


def parse_decision_bands(path: str) -> List[DecisionBand]:
    data = json.loads(read_file(path))
    return [
        DecisionBand(
            min=item["min"],
            max=item["max"],
            decision=item["decision"],
            reason=item["reason"],
        )
        for item in data["bands"]
    ]


def parse_account_profiles(path: str) -> Dict[str, AccountProfile]:
    profiles: Dict[str, AccountProfile] = {}
    for line in read_lines(path):
        item = json.loads(line)
        profile = AccountProfile(account_id=item["account_id"], return_count=item["return_count"])
        profiles[profile.account_id] = profile
    return profiles


def parse_account_links(path: str) -> List[AccountLinkGroup]:
    groups: List[AccountLinkGroup] = []
    for line in read_lines(path):
        item = json.loads(line)
        groups.append(AccountLinkGroup(group_id=item["group_id"], accounts=list(item["accounts"])))
    return groups


def parse_return_requests(path: str) -> List[ReturnRequest]:
    requests: List[ReturnRequest] = []
    for line in read_lines(path):
        item = json.loads(line)
        requests.append(
            ReturnRequest(
                request_id=item["request_id"],
                account_id=item["account_id"],
                category=item["category"],
                days_since_purchase=item["days_since_purchase"],
                order_value_usd=item["order_value_usd"],
                account_age_days=item["account_age_days"],
            )
        )
    return requests


def decision_to_json(decision: ReturnDecision) -> str:
    """Serializes a decision to a compact JSON string, e.g.
    {"request_id":"r101","risk_score":3,"decision":"AUTO_APPROVE"}"""
    payload = {
        "request_id": decision.request_id,
        "risk_score": decision.risk_score,  # None -> serializes as JSON null
        "decision": decision.decision,
    }
    if decision.reason is not None:
        payload["reason"] = decision.reason
    return json.dumps(payload)
