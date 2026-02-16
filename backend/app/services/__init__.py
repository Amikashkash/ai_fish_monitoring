"""Business logic services."""

from app.services.density_calculator import (
    calculate_density,
    assess_density_risk,
    recommend_treatment_intensity
)

from app.services.success_rate_calculator import (
    calculate_success_rate,
    calculate_mortality_rate,
    assess_treatment_effectiveness,
    is_treatment_successful
)

from app.services.treatment_scheduler import (
    get_active_treatments,
    get_treatments_ending_today,
    get_treatments_needing_followup,
    get_daily_treatment_tasks
)

from app.services.supplier_analyzer import (
    analyze_supplier_performance,
    get_supplier_stats,
    get_best_source_for_species
)

from app.services.data_aggregator import (
    aggregate_historical_data,
    build_treatment_summary,
    get_treatment_timeline
)

__all__ = [
    # Density calculator
    "calculate_density",
    "assess_density_risk",
    "recommend_treatment_intensity",
    # Success rate calculator
    "calculate_success_rate",
    "calculate_mortality_rate",
    "assess_treatment_effectiveness",
    "is_treatment_successful",
    # Treatment scheduler
    "get_active_treatments",
    "get_treatments_ending_today",
    "get_treatments_needing_followup",
    "get_daily_treatment_tasks",
    # Supplier analyzer
    "analyze_supplier_performance",
    "get_supplier_stats",
    "get_best_source_for_species",
    # Data aggregator
    "aggregate_historical_data",
    "build_treatment_summary",
    "get_treatment_timeline",
]
