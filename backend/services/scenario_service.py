"""Life-Event Scenario Planning service."""

from decimal import Decimal
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func

from backend.models.user import User
from backend.models.scenario import FinancialScenario
from backend.models.savings import SavingsGoal
from backend.schemas.scenario import (
    LifeEventScenarioRequest,
    LifeEventScenarioResponse,
    ScenarioImpactItem
)
from backend.core.exceptions import NotFoundException
from finance_engine.budgeting.engine import to_decimal


class ScenarioService:
    def __init__(self, db: Session):
        self.db = db

    def evaluate_life_event(
        self,
        user: User,
        payload: LifeEventScenarioRequest,
        save_scenario: bool = True
    ) -> LifeEventScenarioResponse:
        """
        Simulate the financial consequences of a major life event over a defined duration.
        Computes baseline vs scenario cash accumulation, buffer degradation, and sustainability.
        """
        income = to_decimal(user.monthly_income)
        base_surplus = income * Decimal("0.30") if income > Decimal("0.00") else Decimal("1000.00")

        # Scenario adjustments
        scenario_surplus = base_surplus + to_decimal(payload.monthly_income_delta) - to_decimal(payload.monthly_expense_delta)
        one_time = to_decimal(payload.one_time_cost)
        duration = max(1, payload.duration_months)

        # Monthly trajectory over duration
        monthly_projections: List[ScenarioImpactItem] = []
        base_cum = Decimal("0.00")
        scen_cum = -one_time # one-time upfront hit

        for m in range(1, duration + 1):
            base_cum += base_surplus
            scen_cum += scenario_surplus
            monthly_projections.append(
                ScenarioImpactItem(
                    month=m,
                    baseline_cash_balance=base_cum,
                    scenario_cash_balance=scen_cum,
                    difference=scen_cum - base_cum
                )
            )

        total_recurring_impact = (scenario_surplus - base_surplus) * Decimal(str(duration))
        net_wealth_impact = total_recurring_impact - one_time

        # Current liquid emergency buffer
        total_savings = self.db.query(func.sum(SavingsGoal.current_amount)).filter(
            SavingsGoal.user_id == user.id
        ).scalar()
        current_savings = to_decimal(total_savings) if total_savings else Decimal("5000.00")
        
        # Monthly essential living expenses
        essential_burn = (income * Decimal("0.50")) if income > 0 else Decimal("2000.00")
        scenario_burn = essential_burn + max(Decimal("0.00"), to_decimal(payload.monthly_expense_delta))

        # Months buffer lasts under worst case
        buffer_impact_months = float((current_savings - one_time) / scenario_burn) if scenario_burn > 0 else 0.0

        is_sustainable = bool(scen_cum >= Decimal("0.00") and scenario_surplus >= Decimal("0.00"))

        if is_sustainable:
            verdict = "SUSTAINABLE_PLAN"
        elif scen_cum >= Decimal("0.00") and scenario_surplus < Decimal("0.00"):
            verdict = "BUFFER_DEPLETING_TEMPORARY"
        else:
            verdict = "DEFICIT_HIGH_RISK"

        scenario_record_id = None
        if save_scenario:
            db_scen = FinancialScenario(
                user_id=user.id,
                title=payload.title,
                scenario_type=f"life_event_{payload.event_type}",
                description=payload.notes,
                input_parameters=payload.model_dump(mode="json"),
                output_results={
                    "baseline_monthly_surplus": str(base_surplus),
                    "scenario_monthly_surplus": str(scenario_surplus),
                    "net_wealth_impact": str(net_wealth_impact),
                    "is_sustainable": is_sustainable,
                    "verdict": verdict
                }
            )
            self.db.add(db_scen)
            self.db.commit()
            self.db.refresh(db_scen)
            scenario_record_id = db_scen.id

        return LifeEventScenarioResponse(
            id=scenario_record_id,
            title=payload.title,
            event_type=payload.event_type,
            baseline_monthly_surplus=base_surplus,
            scenario_monthly_surplus=scenario_surplus,
            total_one_time_impact=one_time,
            total_recurring_impact=total_recurring_impact,
            net_wealth_impact=net_wealth_impact,
            emergency_buffer_impact_months=round(buffer_impact_months, 1),
            is_sustainable=is_sustainable,
            summary_verdict=verdict,
            monthly_projections=monthly_projections
        )

    def list_saved_scenarios(self, user: User) -> List[FinancialScenario]:
        return self.db.query(FinancialScenario).filter(
            FinancialScenario.user_id == user.id
        ).order_by(FinancialScenario.created_at.desc()).all()
