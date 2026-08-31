

from dataclasses import dataclass, field
from typing import List, Optional, Dict


@dataclass
class CategoryRule:
    category: str
    return_window_days: int


@dataclass
class PointBand:
    min: int
    max: int
    points: int


@dataclass
class ScoringRules:
    return_history_points: List[PointBand] = field(default_factory=list)
    account_age_points: List[PointBand] = field(default_factory=list)
    order_value_points: List[PointBand] = field(default_factory=list)


@dataclass
class DecisionBand:
    min: int
    max: int
    decision: str
    reason: str


@dataclass
class AccountProfile:
    account_id: str
    return_count: int


@dataclass
class AccountLinkGroup:
    group_id: str
    accounts: List[str]


@dataclass
class ReturnRequest:
    request_id: str
    account_id: str
    category: str
    days_since_purchase: int
    order_value_usd: float
    account_age_days: int


@dataclass
class ReturnDecision:
    request_id: str
    risk_score: Optional[int]   # None ("null") when rejected before scoring
    decision: str                # AUTO_APPROVE | MANUAL_REVIEW | REJECT
    reason: Optional[str] = None


@dataclass
class EngineData:
    category_rules: List[CategoryRule] = field(default_factory=list)
    scoring_rules: ScoringRules = field(default_factory=ScoringRules)
    decision_bands: List[DecisionBand] = field(default_factory=list)
    account_profiles: Dict[str, AccountProfile] = field(default_factory=dict)
    account_links: List[AccountLinkGroup] = field(default_factory=list)
