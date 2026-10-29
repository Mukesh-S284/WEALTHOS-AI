"""Financial Learning Coach service with comprehensive curriculum and quiz engine."""

from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
from sqlalchemy.orm import Session

from backend.models.user import User
from backend.models.learning import LearningProgress
from backend.schemas.learning import (
    LessonTopic,
    QuizQuestion,
    QuizSubmissionRequest,
    QuizResultResponse,
    UserLearningProgressResponse
)
from backend.core.exceptions import NotFoundException

CURRICULUM: List[LessonTopic] = [
    LessonTopic(
        id="budgeting_50_30_20",
        title="The 50/30/20 Budgeting Rule",
        category="Foundations",
        read_time_minutes=4,
        summary="Master the gold-standard household budgeting framework dividing income into Needs, Wants, and Savings.",
        content=(
            "### What is the 50/30/20 Rule?\n\n"
            "Popularized by Senator Elizabeth Warren in *All Your Worth*, the 50/30/20 rule is an intuitive budgeting framework:\n\n"
            "1. **50% Needs**: Non-negotiable essentials required to live and work. Includes rent/mortgage, utilities, essential groceries, minimum debt payments, and basic healthcare.\n"
            "2. **30% Wants**: Discretionary spending that enhances quality of life. Dining out, streaming subscriptions, vacations, hobby gear, and entertainment.\n"
            "3. **20% Savings & Debt Acceleration**: Building an emergency cushion, investing in retirement accounts, funding SIPs, and accelerating high-interest debt payoffs.\n\n"
            "### Common Pitfall\n"
            "Treating lifestyle upgrades as 'Needs' (e.g. luxury car leases or premium delivery apps) instead of 'Wants'. Maintain strict honesty in category tagging."
        ),
        quiz=[
            QuizQuestion(
                id="q1",
                question="Under the 50/30/20 rule, which category does a minimum credit card payment belong to?",
                options=["Needs", "Wants", "Discretionary", "Optional"],
                correct_option_index=0,
                explanation="Minimum debt obligations are legal contractual requirements needed to protect your credit and avoid legal default, classifying them as Needs."
            ),
            QuizQuestion(
                id="q2",
                question="What percentage of after-tax income should ideally be allocated to savings and extra debt reduction?",
                options=["5%", "10%", "20%", "50%"],
                correct_option_index=2,
                explanation="20% is the target threshold to ensure steady capital accumulation and retirement readiness."
            ),
            QuizQuestion(
                id="q3",
                question="A dining out meal at an upscale restaurant is categorized as:",
                options=["Need", "Want", "Emergency", "Fixed Expense"],
                correct_option_index=1,
                explanation="While food is essential, dining at restaurants is discretionary and categorized as a Want."
            )
        ]
    ),
    LessonTopic(
        id="emergency_funds",
        title="Emergency Funds & Financial Resilience",
        category="Foundations",
        read_time_minutes=5,
        summary="Learn why an emergency fund is your portfolio's first line of defense against liquidation shocks.",
        content=(
            "### The Purpose of an Emergency Fund\n\n"
            "An emergency fund is a liquid pool of cash set aside exclusively for unexpected life events: medical emergencies, sudden car repairs, or temporary job interruption.\n\n"
            "### How Big Should It Be?\n"
            "- **3 to 6 months of essential living expenses**: Standard for dual-income households with stable corporate jobs.\n"
            "- **6 to 12 months**: Recommended for freelancers, entrepreneurs, single-earner families, or commission-based workers.\n\n"
            "### Where Should You Keep It?\n"
            "In high-yield savings accounts (HYSA) or short-term Treasury/money market funds. It should NEVER be invested in volatile equities or locked into illiquid assets."
        ),
        quiz=[
            QuizQuestion(
                id="q1",
                question="Where should an emergency fund ideally be parked?",
                options=["Cryptocurrency tokens", "Individual tech stocks", "High-Yield Savings Account (HYSA)", "10-year Real Estate syndicate"],
                correct_option_index=2,
                explanation="Emergency funds must prioritize liquidity and principal stability above all else."
            ),
            QuizQuestion(
                id="q2",
                question="Why is investing your emergency fund in stocks dangerous?",
                options=["Stocks never pay dividends", "Market downturns often coincide with job losses, forcing liquidation at market lows", "Banks prohibit stocks", "Taxes are 100%"],
                correct_option_index=1,
                explanation="Economic recessions often lead to simultaneous layoffs and stock market drawdowns, creating a devastating compounding loss if forced to sell."
            ),
            QuizQuestion(
                id="q3",
                question="How many months of essential expenses should a freelance or self-employed worker target?",
                options=["1 month", "2 months", "6 to 12 months", "30 years"],
                correct_option_index=2,
                explanation="Irregular income streams require a larger safety buffer of 6 to 12 months."
            )
        ]
    ),
    LessonTopic(
        id="compound_interest",
        title="Compound Interest & Time Value of Money",
        category="Investing",
        read_time_minutes=4,
        summary="Understand the mathematics of exponential wealth growth and why starting early matters most.",
        content=(
            "### The Exponential Nature of Compounding\n\n"
            "Compound interest is interest calculated on the initial principal and also on the accumulated interest of previous periods.\n\n"
            "The Rule of 72:\n"
            "To estimate the years required to double your money, divide 72 by your annual interest rate.\n"
            "Example: At an 8% annual return, $72 / 8 = 9$ years to double your investment.\n\n"
            "Starting 10 years earlier at age 25 rather than age 35 can double or triple final retirement wealth, even with smaller monthly contributions."
        ),
        quiz=[
            QuizQuestion(
                id="q1",
                question="Using the Rule of 72, how many years does it take to double money at a 6% annual return?",
                options=["6 years", "12 years", "18 years", "24 years"],
                correct_option_index=1,
                explanation="72 divided by 6 equals 12 years."
            ),
            QuizQuestion(
                id="q2",
                question="Which factor has the greatest multiplier effect on compound growth?",
                options=["Checking account interest", "Time (number of compounding years)", "Paying bank transaction fees", "Day-trading every hour"],
                correct_option_index=1,
                explanation="Time is an exponent in the compounding equation; starting early produces exponential multiplier benefits."
            ),
            QuizQuestion(
                id="q3",
                question="What is the key difference between simple and compound interest?",
                options=["Simple interest grows exponentially", "Compound interest pays interest on previously earned interest", "There is no difference", "Simple interest is only for crypto"],
                correct_option_index=1,
                explanation="Compound interest continuously reinvests earnings to generate further earnings."
            )
        ]
    ),
    LessonTopic(
        id="debt_strategies",
        title="Debt Payoff: Avalanche vs Snowball",
        category="Debt Management",
        read_time_minutes=5,
        summary="Compare the mathematically optimal Avalanche method against the psychologically rewarding Snowball method.",
        content=(
            "### The Two Standard Payoff Methods\n\n"
            "1. **Debt Avalanche (Highest APR First)**:\n"
            "You pay minimums on all liabilities, then direct all surplus cash to the debt with the highest interest rate (e.g. a 24% APR credit card). Mathematically, this minimizes total interest paid and clears debt fastest.\n\n"
            "2. **Debt Snowball (Lowest Balance First)**:\n"
            "You pay minimums on all debts, then target the smallest dollar balance regardless of APR. Eliminating small debts quickly provides psychological momentum and frees up cash flow early."
        ),
        quiz=[
            QuizQuestion(
                id="q1",
                question="Which debt repayment strategy mathematically minimizes the total interest you pay?",
                options=["Debt Snowball", "Debt Avalanche", "Equal Split Method", "Random Allocation"],
                correct_option_index=1,
                explanation="The Avalanche method aggressively tackles the highest interest rates first, directly minimizing cumulative interest costs."
            ),
            QuizQuestion(
                id="q2",
                question="What is the primary psychological advantage of the Debt Snowball method?",
                options=["Guarantees 0% APR", "Provides quick early wins by completely eliminating smaller debts", "Erases debt from credit reports", "Doubles your credit card limit"],
                correct_option_index=1,
                explanation="The Snowball method builds habit momentum by knocking out individual debts quickly."
            ),
            QuizQuestion(
                id="q3",
                question="When debt liabilities are paid off, what happens to freed cash flow?",
                options=["It vanishes", "It is rolled over into the next target debt (snowballing your payments)", "It must be donated", "It triggers immediate penalty fees"],
                correct_option_index=1,
                explanation="The freed cash flow increases the monthly payment available for the next debt in line."
            )
        ]
    ),
    LessonTopic(
        id="sips_dollar_cost_averaging",
        title="Systematic Investment Plans & Dollar-Cost Averaging",
        category="Investing",
        read_time_minutes=5,
        summary="Understand how periodic automated investing smooths volatility and eliminates market-timing pitfalls.",
        content=(
            "### What is Dollar-Cost Averaging (DCA)?\n\n"
            "Dollar-cost averaging involves investing equal monetary amounts at regular, predetermined intervals (e.g., monthly) regardless of market swings.\n\n"
            "### Mechanics\n"
            "- When unit prices are low, your fixed contribution acquires more units.\n"
            "- When unit prices are high, your fixed contribution buys fewer units.\n"
            "- Over market cycles, your average purchase price per unit tends to be lower than the average market price over the period.\n\n"
            "### Why Avoid Market Timing?\n"
            "Academic research consistently shows that trying to predict short-term peaks and troughs underperforms disciplined, automated recurring investing."
        ),
        quiz=[
            QuizQuestion(
                id="q1",
                question="What happens during a market downturn when investing via SIP / Dollar-Cost Averaging?",
                options=["Your recurring investment buys more units at lower prices", "Your account is frozen", "All previous gains are automatically deleted", "You are forced to sell your holdings"],
                correct_option_index=0,
                explanation="Fixed monthly investments purchase more units when asset prices fall, lowering your average cost per unit."
            ),
            QuizQuestion(
                id="q2",
                question="What is the primary behavioral benefit of automated SIP investing?",
                options=["It guarantees doubling money in 1 month", "It eliminates emotional temptation to time volatile market swings", "It provides 100% tax exemption on all income", "It replaces the need for an emergency fund"],
                correct_option_index=1,
                explanation="Automated periodic contributions remove emotional fear and greed from the investment process."
            )
        ]
    ),
    LessonTopic(
        id="asset_allocation_risk",
        title="Asset Allocation & Portfolio Diversification",
        category="Investing",
        read_time_minutes=6,
        summary="Explore how balancing equities, fixed income, cash, and commodities protects against catastrophic drawdowns.",
        content=(
            "### The Principle of Asset Allocation\n\n"
            "Over 90% of long-term portfolio return variability is driven by asset allocation (how much you allocate across stocks, bonds, cash, and real assets), rather than individual stock picking.\n\n"
            "### Uncorrelated Assets\n"
            "By pairing assets whose price movements do not move in perfect tandem (e.g., stocks and high-grade government bonds), you achieve higher risk-adjusted returns (higher Sharpe ratio) and reduced portfolio volatility."
        ),
        quiz=[
            QuizQuestion(
                id="q1",
                question="According to modern portfolio theory, what primarily drives long-term portfolio volatility and returns?",
                options=["Day trading frequency", "Asset allocation across broad classes", "Buying penny stocks", "Following social media trends"],
                correct_option_index=1,
                explanation="Broad asset allocation across equities, fixed income, and cash drives over 90% of portfolio performance variance."
            ),
            QuizQuestion(
                id="q2",
                question="What is the core benefit of holding uncorrelated assets in a portfolio?",
                options=["Guarantees 0% drawdowns in all market crashes", "Reduces overall portfolio volatility while preserving expected returns", "Guarantees you never have to pay taxes", "Triples dividends immediately"],
                correct_option_index=1,
                explanation="When assets are uncorrelated, one asset can buffer losses while another rises, smoothing portfolio drawdowns."
            )
        ]
    ),
    LessonTopic(
        id="crypto_volatility_risks",
        title="Cryptocurrency Risks, Volatility & Custody",
        category="Advanced",
        read_time_minutes=5,
        summary="Examine extreme volatility, smart contract risk, lack of deposit insurance, and self-custody principles.",
        content=(
            "### Understanding Cryptocurrency Risk Profile\n\n"
            "Crypto assets exhibit annual volatility exceeding 50% to 80%, with historical drawdowns exceeding 70% to 85% during bear cycles.\n\n"
            "### Key Risk Factors\n"
            "1. **No Deposit Insurance**: Unlike bank deposits insured up to regulatory limits (e.g. FDIC), crypto assets held on exchanges carry counterparty insolvency risk.\n"
            "2. **Irreversible Transactions**: Erroneous transfers or compromise of private keys cannot be reversed by customer support.\n"
            "3. **Prudent Sizing**: Prudent risk management typically caps speculative digital assets at 1% to 5% of total liquid net worth."
        ),
        quiz=[
            QuizQuestion(
                id="q1",
                question="Are cryptocurrency deposits on centralized trading exchanges protected by government deposit insurance like FDIC?",
                options=["Yes, up to $250,000", "No, cryptocurrency accounts are generally not covered by government deposit insurance", "Yes, covered by global blockchain insurance", "Yes, fully guaranteed by central banks"],
                correct_option_index=1,
                explanation="Crypto assets held on commercial exchanges carry counterparty risk and do not enjoy federal deposit insurance."
            ),
            QuizQuestion(
                id="q2",
                question="What is a generally recommended risk-management guideline for speculative digital assets in a long-term portfolio?",
                options=["100% of emergency fund", "50% to 80% of net worth", "A modest cap such as 1% to 5% of total portfolio", "Never keep cash; hold only crypto"],
                correct_option_index=2,
                explanation="Capping speculative volatile holdings at 1-5% prevents crypto market crashes from threatening core financial survival."
            )
        ]
    )
]


class LearningService:
    def __init__(self, db: Session):
        self.db = db

    def list_topics(self, user: User) -> List[UserLearningProgressResponse]:
        """List all curriculum topics along with the user's progress and quiz scores."""
        progress_records = self.db.query(LearningProgress).filter(
            LearningProgress.user_id == user.id
        ).all()
        prog_map = {p.topic_id: p for p in progress_records}

        results = []
        for t in CURRICULUM:
            p = prog_map.get(t.id)
            results.append(
                UserLearningProgressResponse(
                    topic_id=t.id,
                    title=t.title,
                    completed=p.completed if p else False,
                    quiz_score=p.quiz_score if p else None,
                    quiz_attempts=p.quiz_attempts if p else 0,
                    last_studied_at=p.last_studied_at.isoformat() if p else None
                )
            )
        return results

    def get_topic(self, topic_id: str) -> LessonTopic:
        t = next((item for item in CURRICULUM if item.id == topic_id), None)
        if not t:
            raise NotFoundException("Lesson Topic", topic_id)
        return t

    def submit_quiz(self, user: User, payload: QuizSubmissionRequest) -> QuizResultResponse:
        """Grade quiz, store progress and score in database, and return detailed answer feedback."""
        topic = self.get_topic(payload.topic_id)
        correct_count = 0
        details = []

        for q in topic.quiz:
            user_choice = payload.selected_answers.get(q.id)
            is_correct = (user_choice == q.correct_option_index)
            if is_correct:
                correct_count += 1
            details.append({
                "question_id": q.id,
                "question": q.question,
                "user_choice": user_choice,
                "correct_option_index": q.correct_option_index,
                "is_correct": is_correct,
                "explanation": q.explanation
            })

        total_q = len(topic.quiz)
        score_pct = int((correct_count / total_q) * 100) if total_q > 0 else 100
        passed = score_pct >= 66

        # Update or create progress in DB
        prog = self.db.query(LearningProgress).filter(
            LearningProgress.user_id == user.id,
            LearningProgress.topic_id == topic.id
        ).first()

        now = datetime.now(timezone.utc)
        if not prog:
            prog = LearningProgress(
                user_id=user.id,
                topic_id=topic.id,
                completed=passed,
                quiz_score=score_pct,
                quiz_attempts=1,
                last_studied_at=now
            )
            self.db.add(prog)
        else:
            prog.quiz_attempts += 1
            prog.last_studied_at = now
            if score_pct > (prog.quiz_score or 0):
                prog.quiz_score = score_pct
            if passed:
                prog.completed = True

        self.db.commit()

        return QuizResultResponse(
            topic_id=topic.id,
            total_questions=total_q,
            correct_count=correct_count,
            score_percentage=score_pct,
            passed=passed,
            question_results=details
        )
