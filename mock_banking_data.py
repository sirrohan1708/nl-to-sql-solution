"""
Mock Banking Database - Dummy Data for Client Presentation
============================================================
Contains realistic banking data for demonstrating NL to SQL capabilities.
Includes customers, accounts, transactions, and loans data.
"""

from datetime import datetime, timedelta
import random

# ============================================================================
# Banking Mock Data Generator
# ============================================================================

def generate_mock_customers():
    """Generate 100 mock banking customers"""
    first_names = [
        "James", "Mary", "John", "Patricia", "Robert", "Jennifer", "Michael", "Linda",
        "William", "Barbara", "David", "Elizabeth", "Richard", "Susan", "Joseph", "Jessica",
        "Thomas", "Sarah", "Charles", "Karen", "Christopher", "Nancy", "Daniel", "Lisa",
        "Matthew", "Betty", "Anthony", "Margaret", "Mark", "Sandra", "Donald", "Ashley",
        "Steven", "Kimberly", "Paul", "Emily", "Andrew", "Donna", "Joshua", "Michelle",
        "Kenneth", "Carol", "Kevin", "Amanda", "Brian", "Dorothy", "George", "Melissa",
        "Edward", "Deborah", "Ronald", "Stephanie", "Timothy", "Rebecca", "Jason", "Sharon",
        "Jeffrey", "Laura", "Ryan", "Cynthia", "Jacob", "Kathleen", "Gary", "Amy",
        "Nicholas", "Shirley", "Eric", "Angela", "Jonathan", "Helen", "Stephen", "Anna",
        "Larry", "Brenda", "Justin", "Pamela", "Scott", "Nicole", "Brandon", "Emma",
        "Benjamin", "Samantha", "Samuel", "Katherine", "Raymond", "Christine", "Gregory", "Debra",
        "Frank", "Rachel", "Alexander", "Catherine", "Patrick", "Carolyn", "Jack", "Janet"
    ]
    
    last_names = [
        "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis",
        "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzalez", "Wilson", "Anderson", "Thomas",
        "Taylor", "Moore", "Jackson", "Martin", "Lee", "Perez", "Thompson", "White",
        "Harris", "Sanchez", "Clark", "Ramirez", "Lewis", "Robinson", "Walker", "Young",
        "Allen", "King", "Wright", "Scott", "Torres", "Nguyen", "Hill", "Flores",
        "Green", "Adams", "Nelson", "Baker", "Hall", "Rivera", "Campbell", "Mitchell",
        "Carter", "Roberts", "Gomez", "Phillips", "Evans", "Turner", "Diaz", "Parker",
        "Cruz", "Edwards", "Collins", "Reyes", "Stewart", "Morris", "Morales", "Murphy",
        "Cook", "Rogers", "Gutierrez", "Ortiz", "Morgan", "Cooper", "Peterson", "Bailey",
        "Reed", "Kelly", "Howard", "Ramos", "Kim", "Cox", "Ward", "Richardson",
        "Watson", "Brooks", "Chavez", "Wood", "James", "Bennett", "Gray", "Mendoza",
        "Ruiz", "Hughes", "Price", "Alvarez", "Castillo", "Sanders", "Patel", "Myers"
    ]
    
    cities = [
        "New York", "Los Angeles", "Chicago", "Houston", "Phoenix", "Philadelphia",
        "San Antonio", "San Diego", "Dallas", "San Jose", "Austin", "Jacksonville",
        "Fort Worth", "Columbus", "Charlotte", "San Francisco", "Indianapolis", "Seattle",
        "Denver", "Boston", "Nashville", "Detroit", "Portland", "Las Vegas", "Miami"
    ]
    
    account_types = ["Savings", "Checking", "Premium Checking", "Business", "Student"]
    customer_segments = ["Retail", "Premium", "Business", "Corporate", "Student"]
    
    customers = []
    base_date = datetime(2020, 1, 1)
    
    for i in range(1, 101):
        days_offset = random.randint(0, 1800)  # Up to 5 years ago
        signup_date = base_date + timedelta(days=days_offset)
        
        # Generate credit score based on segment
        segment = random.choice(customer_segments)
        if segment in ["Premium", "Corporate"]:
            credit_score = random.randint(720, 850)
        elif segment == "Business":
            credit_score = random.randint(680, 800)
        else:
            credit_score = random.randint(600, 780)
        
        customer = {
            "customer_id": i,
            "first_name": random.choice(first_names),
            "last_name": random.choice(last_names),
            "email": f"customer{i}@email.com",
            "phone": f"+1-555-{random.randint(100, 999)}-{random.randint(1000, 9999)}",
            "city": random.choice(cities),
            "state": "NY" if random.random() > 0.7 else random.choice(["CA", "TX", "FL", "IL"]),
            "account_type": random.choice(account_types),
            "customer_segment": segment,
            "credit_score": credit_score,
            "signup_date": signup_date.strftime("%Y-%m-%d"),
            "account_balance": round(random.uniform(500, 250000), 2),
            "is_active": random.choice([True, True, True, False])  # 75% active
        }
        customers.append(customer)
    
    return customers


def generate_mock_transactions(customers):
    """Generate realistic banking transactions"""
    transaction_types = [
        "ATM Withdrawal", "Deposit", "Wire Transfer", "Check Deposit", 
        "Online Transfer", "POS Purchase", "Bill Payment", "Direct Deposit",
        "Mobile Payment", "ACH Transfer", "International Wire", "Cashback"
    ]
    
    transaction_categories = [
        "Groceries", "Utilities", "Rent", "Salary", "Healthcare", "Entertainment",
        "Transportation", "Dining", "Shopping", "Insurance", "Investment", "Education"
    ]
    
    statuses = ["completed", "completed", "completed", "pending", "failed"]
    
    transactions = []
    transaction_id = 1
    base_date = datetime(2024, 1, 1)
    
    # Generate 5-15 transactions per customer
    for customer in customers:
        num_transactions = random.randint(5, 15)
        customer_id = customer["customer_id"]
        
        for _ in range(num_transactions):
            days_offset = random.randint(0, 310)  # Last ~10 months
            txn_date = base_date + timedelta(days=days_offset)
            
            txn_type = random.choice(transaction_types)
            status = random.choice(statuses)
            
            # Amount based on transaction type
            if txn_type in ["Salary", "Direct Deposit"]:
                amount = round(random.uniform(2000, 8000), 2)
            elif txn_type in ["Rent", "Insurance"]:
                amount = round(random.uniform(800, 3000), 2)
            elif txn_type in ["Wire Transfer", "International Wire"]:
                amount = round(random.uniform(500, 15000), 2)
            elif txn_type == "ATM Withdrawal":
                amount = round(random.choice([20, 40, 60, 80, 100, 200]), 2)
            else:
                amount = round(random.uniform(10, 500), 2)
            
            transaction = {
                "transaction_id": transaction_id,
                "customer_id": customer_id,
                "transaction_type": txn_type,
                "category": random.choice(transaction_categories),
                "amount": amount,
                "currency": "USD",
                "transaction_date": txn_date.strftime("%Y-%m-%d"),
                "transaction_time": f"{random.randint(0, 23):02d}:{random.randint(0, 59):02d}:{random.randint(0, 59):02d}",
                "status": status,
                "merchant": f"Merchant_{random.randint(1, 50)}",
                "location": random.choice(["New York, NY", "Los Angeles, CA", "Chicago, IL", "Houston, TX", "Online"]),
                "description": f"{txn_type} - {random.choice(transaction_categories)}"
            }
            transactions.append(transaction)
            transaction_id += 1
    
    return transactions


def generate_mock_loans(customers):
    """Generate loan data for banking customers"""
    loan_types = [
        "Personal Loan", "Home Mortgage", "Auto Loan", 
        "Business Loan", "Student Loan", "Credit Card"
    ]
    
    loan_statuses = ["Active", "Active", "Active", "Paid Off", "Defaulted", "Pending"]
    
    loans = []
    loan_id = 1
    
    # 60% of customers have loans
    loan_customers = random.sample(customers, k=60)
    
    for customer in loan_customers:
        # Each customer may have 1-3 loans
        num_loans = random.randint(1, 3)
        
        for _ in range(num_loans):
            loan_type = random.choice(loan_types)
            status = random.choice(loan_statuses)
            
            # Loan amount based on type
            if loan_type == "Home Mortgage":
                principal = round(random.uniform(150000, 500000), 2)
                interest_rate = round(random.uniform(3.5, 6.5), 2)
                term_months = random.choice([180, 240, 360])  # 15, 20, 30 years
            elif loan_type == "Auto Loan":
                principal = round(random.uniform(15000, 60000), 2)
                interest_rate = round(random.uniform(4.0, 8.0), 2)
                term_months = random.choice([36, 48, 60, 72])
            elif loan_type == "Business Loan":
                principal = round(random.uniform(25000, 200000), 2)
                interest_rate = round(random.uniform(5.5, 12.0), 2)
                term_months = random.choice([36, 60, 84, 120])
            elif loan_type == "Student Loan":
                principal = round(random.uniform(10000, 80000), 2)
                interest_rate = round(random.uniform(3.0, 6.5), 2)
                term_months = random.choice([120, 180, 240])
            else:  # Personal Loan or Credit Card
                principal = round(random.uniform(5000, 35000), 2)
                interest_rate = round(random.uniform(8.0, 18.0), 2)
                term_months = random.choice([24, 36, 48, 60])
            
            # Calculate remaining balance
            months_elapsed = random.randint(1, min(term_months, 60))
            if status == "Paid Off":
                outstanding_balance = 0.0
            elif status == "Defaulted":
                outstanding_balance = principal * random.uniform(0.4, 0.9)
            else:
                outstanding_balance = principal * (1 - (months_elapsed / term_months))
            
            start_date = datetime(2020, 1, 1) + timedelta(days=random.randint(0, 1400))
            
            loan = {
                "loan_id": loan_id,
                "customer_id": customer["customer_id"],
                "loan_type": loan_type,
                "principal_amount": round(principal, 2),
                "outstanding_balance": round(outstanding_balance, 2),
                "interest_rate": interest_rate,
                "term_months": term_months,
                "monthly_payment": round(principal * (interest_rate/100/12) / (1 - (1 + interest_rate/100/12)**(-term_months)), 2),
                "start_date": start_date.strftime("%Y-%m-%d"),
                "status": status,
                "credit_score_at_approval": customer["credit_score"] + random.randint(-30, 10)
            }
            loans.append(loan)
            loan_id += 1
    
    return loans


# ============================================================================
# Generate All Mock Data
# ============================================================================

# Generate the data
MOCK_CUSTOMERS = generate_mock_customers()
MOCK_TRANSACTIONS = generate_mock_transactions(MOCK_CUSTOMERS)
MOCK_LOANS = generate_mock_loans(MOCK_CUSTOMERS)

print(f"Generated {len(MOCK_CUSTOMERS)} customers")
print(f"Generated {len(MOCK_TRANSACTIONS)} transactions")
print(f"Generated {len(MOCK_LOANS)} loans")
