"""Curated labeled dataset of financial transaction descriptions for categorization."""

from typing import List, Tuple

# Diverse, realistic dataset of transaction descriptions paired with standard categories
DATASET: List[Tuple[str, str]] = [
    # Groceries
    ("WHOLE FOODS MARKET SOMA SAN FRANCISCO CA", "Groceries"),
    ("TRADER JOE'S #501 ARLINGTON VA", "Groceries"),
    ("SAFEWAY STORE 1284 BERKELEY CA", "Groceries"),
    ("KROGER #042 GROCERY STORE ATLANTA GA", "Groceries"),
    ("WAL-MART SUPERCENTER GROCERY DALLAS TX", "Groceries"),
    ("ALDI GROCERY STORE CHICAGO IL", "Groceries"),
    ("COSTCO WHOLESALE WAREHOUSE SEATTLE WA", "Groceries"),
    ("TARGET SUPERSTORE T-1402 MINNEAPOLIS MN", "Groceries"),
    ("SPROUTS FARMERS MARKET DENVER CO", "Groceries"),
    ("HEB GROCERY #221 AUSTIN TX", "Groceries"),
    ("LOCAL ORGANIC MARKET NEW YORK NY", "Groceries"),
    ("FRESH MARKET STORE #84 MIAMI FL", "Groceries"),
    
    # Dining & Restaurants
    ("STARBUCKS STORE 08472 SEATTLE WA", "Dining"),
    ("CHIPOTLE ONLINE ORDER 8394 DENVER CO", "Dining"),
    ("MCDONALDS F1284 CHICAGO IL", "Dining"),
    ("PANERA BREAD #2019 BOSTON MA", "Dining"),
    ("SWEETGREEN SALAD BAR NEW YORK NY", "Dining"),
    ("UBER EATS RESTAURANT DELIVERY", "Dining"),
    ("DOORDASH*FIVE GUYS BURGERS", "Dining"),
    ("SHAKE SHACK #018 MADISON SQUARE", "Dining"),
    ("BLUE BOTTLE COFFEE OAKLAND CA", "Dining"),
    ("DOMINO'S PIZZA ONLINE ORDER", "Dining"),
    ("SUBWAY SANDWICH SHOP #4928", "Dining"),
    ("SUSHI BAR & BISTRO SAN JOSE CA", "Dining"),
    ("TACO BELL MEXICAN RESTAURANT", "Dining"),
    ("ITALIAN RESTAURANT DINNER TRATTORIA", "Dining"),

    # Housing & Rent
    ("AVALON PROPERTY MGMT APARTMENT RENT", "Housing"),
    ("EQUITY RESIDENTIAL MONTHLY RENT ACH", "Housing"),
    ("GREYSTAR MANAGEMENT RENTAL PAYMENT", "Housing"),
    ("MORTGAGE PAYMENT CHASE HOME FINANCE", "Housing"),
    ("WELLS FARGO HOME MORTGAGE ESCROW", "Housing"),
    ("HOA MONTHLY COMMUNITY ASSESSMENT", "Housing"),
    ("RENT PAYMENT VIA VENMO TO LANDLORD", "Housing"),
    ("PROPERTY TAX TOWN OF CAMBRIDGE", "Housing"),

    # Utilities
    ("PACIFIC GAS & ELECTRIC ELECTRIC UTILITY", "Utilities"),
    ("CON EDISON NY UTILITY BILL", "Utilities"),
    ("AT&T WIRELESS MONTHLY CELL PHONE", "Utilities"),
    ("VERIZON WIRELESS BILL PAYMENT", "Utilities"),
    ("COMCAST XFINITY INTERNET CABLE", "Utilities"),
    ("SPECTRUM INTERNET BROADBAND BILL", "Utilities"),
    ("CITY WATER AND SEWER UTILITY", "Utilities"),
    ("WASTE MANAGEMENT TRASH SERVICE", "Utilities"),
    ("T-MOBILE POSTPAID RECURRING BILL", "Utilities"),

    # Transportation & Travel
    ("SHELL OIL 57544329241 SAN FRANCISCO CA", "Transportation"),
    ("CHEVRON FUEL GAS STATION OAKLAND CA", "Transportation"),
    ("EXXONMOBIL HIGHWAY SERVICE STATION", "Transportation"),
    ("UBER TRIP HELP.UBER.COM RIDE", "Transportation"),
    ("LYFT *RIDE MON 8AM SAN FRANCISCO", "Transportation"),
    ("MTA SUBWAY METROCARD RECHARGE NYC", "Transportation"),
    ("BART TICKET CLIPPER CARD RECHARGE", "Transportation"),
    ("DELTA AIR LINES TICKET PURCHASE", "Transportation"),
    ("UNITED AIRLINES FLIGHT BOOKING", "Transportation"),
    ("EZPASS TOLL VIOLATIONS / TOLLWAY", "Transportation"),
    ("ENTERPRISE RENT-A-CAR AIRPORT", "Transportation"),

    # Entertainment & Subscriptions
    ("NETFLIX.COM DIGITAL SUBSCRIPTION", "Subscriptions"),
    ("SPOTIFY USA MONTHLY PREMIUM", "Subscriptions"),
    ("APPLE.COM/BILL ICLOUD SUBSCRIPTION", "Subscriptions"),
    ("GOOGLE *YOUTUBE PREMIUM SUBSCRIPTION", "Subscriptions"),
    ("AMZN DIGITAL*PRIME VIDEO MEMBERSHIP", "Subscriptions"),
    ("NEW YORK TIMES DIGITAL NEWS SUB", "Subscriptions"),
    ("DISNEY PLUS MONTHLY STREAMING", "Subscriptions"),
    ("HBO MAX STREAMING SERVICE WARNER", "Subscriptions"),
    ("GITHUB *COPILOT DEVELOPER SUB", "Subscriptions"),
    ("CHATGPT SUBSCRIPTION OPENAI", "Subscriptions"),

    # Shopping
    ("AMAZON.COM*RT984 MARKETPLACE", "Shopping"),
    ("BEST BUY #0948 ELECTRONICS STORE", "Shopping"),
    ("APPLE STORE RETAIL FIFTH AVE NYC", "Shopping"),
    ("ZARA FASHION CLOTHING STORE", "Shopping"),
    ("H&M APPAREL STORE SAN FRANCISCO", "Shopping"),
    ("NIKE FACTORY OUTLET SHOES", "Shopping"),
    ("IKEA FURNITURE STORE HOME GOODS", "Shopping"),
    ("HOME DEPOT STORE #4912 TOOLS", "Shopping"),
    ("SEPHORA COSMETICS BEAUTY STORE", "Shopping"),
    ("NORDSTROM DEPARTMENT STORE", "Shopping"),

    # Healthcare & Medical
    ("CVS PHARMACY STORE #08432", "Healthcare"),
    ("WALGREENS DRUGSTORE PRESCRIPTION", "Healthcare"),
    ("KAISER PERMANENTE MEDICAL COPAY", "Healthcare"),
    ("QUEST DIAGNOSTICS LAB WORK", "Healthcare"),
    ("DENTAL CARE ASSOCIATES CLEANING", "Healthcare"),
    ("EYE CLINIC VISION EXAM DOCTOR", "Healthcare"),
    ("URGENT CARE CLINIC COPAYMENT", "Healthcare"),

    # Income & Salary
    ("PAYROLL DIRECT DEP ACME CORP SALARY", "Income"),
    ("DIRECT DEPOSIT TECH CORP PAYROLL", "Income"),
    ("EMPLOYER DIRECT DEP BIWEEKLY PAY", "Income"),
    ("STRIPE PAYOUT CONSULTING REVENUE", "Income"),
    ("UPWORK ESCROW FREELANCE DISBURSEMENT", "Income"),
    ("IRS TREAS TAX REFUND DIRECT DEP", "Income"),
    ("STATE TREASURY TAX REFUND", "Income"),
    ("BONUS PAYROLL RETENTION DISBURSEMENT", "Income"),

    # Investments & Savings
    ("VANGUARD BUY INDEX FUND VTSAX", "Investments"),
    ("FIDELITY INVESTMENTS BROKERAGE TRANSFER", "Investments"),
    ("SCHWAB BROKERAGE ACH DEPOSIT", "Investments"),
    ("ROBINHOOD FUNDS TRANSFER DEPOSIT", "Investments"),
    ("COINBASE.COM CRYPTO PURCHASE BTC", "Investments"),
]


def get_labeled_data() -> Tuple[List[str], List[str]]:
    """Return texts and labels for training/evaluation."""
    texts = [item[0] for item in DATASET]
    labels = [item[1] for item in DATASET]
    return texts, labels
