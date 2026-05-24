from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import date

class GameRulesSchema(BaseModel):
    name: str
    pick_count: int
    number_range: List[int]
    bonus_count: int
    bonus_range: Optional[List[int]] = None
    prize_tiers: List[int]
    ticket_price: float
    currency: str

class GameSummary(BaseModel):
    name: str
    description: str = ""
    last_draw_id: Optional[int] = None
    last_draw_date: Optional[date] = None
    total_draws: int = 0

class AnalysisResultSchema(BaseModel):
    game: str
    draw_count: int
    hot_numbers: List[int]
    cold_numbers: List[int]
    expected_frequency: float
    chi_squared_p_value: float
    is_predictive: bool
    summary: str

class SuggestionRequest(BaseModel):
    strategy: str = "weighted"
    count: int = 1
    temperature: float = 1.0
    history_limit: Optional[int] = None
    seed: Optional[int] = None
    pick: Optional[int] = None
    pool: Optional[List[int]] = None
    key: Optional[List[int]] = None
    filters: Optional[List[str]] = None
    full_name: Optional[str] = None
    birth_date: Optional[str] = None
    topic: Optional[str] = None
    adaptive_window: bool = False

class SuggestionResponse(BaseModel):
    tickets: List[List[int]]
    confidence: float
    metadata: Dict[str, Any]
    strategy_used: str

class BacktestRequest(BaseModel):
    strategy: str = "weighted"
    draw_ids: Optional[str] = None
    prev: Optional[str] = None
    count: int = 1
    temperature: float = 0.0
    limit: Optional[int] = None
    summary: bool = True
    show_map: bool = False

class CheckRequest(BaseModel):
    numbers: List[int]
    show_range: bool = False

class OddsTier(BaseModel):
    tier: int
    probability: float
    odds_1_in_x: float

class OddsResponse(BaseModel):
    game: str
    tiers: List[OddsTier]
    ticket_price: float
    currency: str

class PruningMetricsSchema(BaseModel):
    strategy_name: str
    lift_over_random: float
    avg_rank: float
    best_hit: int
    is_hibernated: bool

class PruningResponse(BaseModel):
    game: str
    window: int
    threshold: float
    metrics: List[PruningMetricsSchema]

class CalibrateRequest(BaseModel):
    draws: int = 15
    strategies: str = "default"
    limit: int = 50
    min_training: int = 30

class TuneRequest(BaseModel):
    draws: int = 30
    limit: int = 50
    strategies: str = "statistical"
    metric: str = "lift"
    top: int = 1
