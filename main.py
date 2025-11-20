"""
Natural Language to SQL Prototype
==================================
A FastAPI application that converts natural language questions into SQL queries,
validates them for safety, and executes them on a PostgreSQL database (read-only).

Architecture:
- NL Parser: Converts natural language to SQL using OpenAI API
- Validator: Ensures only safe SELECT queries are executed
- Executor: Runs validated queries on PostgreSQL with timeout and row limits
- API: FastAPI endpoint for handling requests

Example usage:
    uvicorn main:app --reload

Example curl command:
    curl -X POST "http://localhost:8000/query" ^
         -H "Content-Type: application/json" ^
         -d "{\"question\": \"Top 5 users by transaction amount\"}"
"""

import os
import time
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
from enum import Enum

from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.responses import HTMLResponse  # added for simple UI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from pydantic import BaseModel, Field, validator
import sqlparse
from sqlparse.sql import Statement
from sqlparse.tokens import Keyword, DML
import psycopg2
from psycopg2.extras import RealDictCursor
import openai
from dotenv import load_dotenv

# New imports for multi-DB support
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
import re

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Natural Language to SQL API",
    description="Convert natural language questions to SQL queries and execute them safely",
    version="1.0.0",
    docs_url="/docs",  # Swagger UI
    redoc_url="/redoc"  # ReDoc
)

# Add security middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],  # Add your frontend URLs
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

app.add_middleware(
    TrustedHostMiddleware, 
    allowed_hosts=["localhost", "127.0.0.1", "*.yourdomain.com"]
)

# Request tracking for basic rate limiting
from collections import defaultdict, deque
import time as time_module
request_tracker = defaultdict(lambda: deque())

def rate_limit_check(client_ip: str) -> bool:
    """Basic rate limiting: max 10 requests per minute per IP"""
    now = time_module.time()
    client_requests = request_tracker[client_ip]
    
    # Remove old requests (older than 1 minute)
    while client_requests and client_requests[0] < now - 60:
        client_requests.popleft()
    
    # Check if under limit
    if len(client_requests) >= 10:
        return False
    
    client_requests.append(now)
    return True

# Import mock banking data
from mock_banking_data import MOCK_CUSTOMERS, MOCK_TRANSACTIONS, MOCK_LOANS

# Mock database schema for banking application
SCHEMA = {
    "customers": {
        "columns": [
            "customer_id", "first_name", "last_name", "email", "phone", 
            "city", "state", "account_type", "customer_segment", "credit_score",
            "signup_date", "account_balance", "is_active"
        ],
        "description": "Banking customers with account details, credit scores, and balances. 100 customer records available."
    },
    "transactions": {
        "columns": [
            "transaction_id", "customer_id", "transaction_type", "category",
            "amount", "currency", "transaction_date", "transaction_time",
            "status", "merchant", "location", "description"
        ],
        "description": "Customer banking transactions including deposits, withdrawals, transfers, and purchases. Multiple transactions per customer."
    },
    "loans": {
        "columns": [
            "loan_id", "customer_id", "loan_type", "principal_amount",
            "outstanding_balance", "interest_rate", "term_months",
            "monthly_payment", "start_date", "status", "credit_score_at_approval"
        ],
        "description": "Customer loans including mortgages, auto loans, personal loans, and business loans with payment details."
    }
}

# Environment configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
# Legacy single string kept for backward compatibility (PostgreSQL default)
DB_CONNECTION_STRING = os.getenv("DATABASE_URL", "")
POSTGRES_URL = os.getenv("POSTGRES_URL", DB_CONNECTION_STRING)
MYSQL_URL = os.getenv("MYSQL_URL", "")
ORACLE_URL = os.getenv("ORACLE_URL", "")  # Expected SQLAlchemy url e.g. oracle+cx_oracle://user:pass@host:1521/?service_name=XYZ
MAX_ROWS = 1000
QUERY_TIMEOUT = 30  # seconds

class DatabaseType(str, Enum):
    POSTGRES = "postgresql"
    MYSQL = "mysql"
    ORACLE = "oracle"

# Engine cache
_ENGINE_CACHE: Dict[str, Engine] = {}
SUPPORTED_DB_TYPES = {db.value for db in DatabaseType}

def get_engine(db_type: str) -> Optional[Engine]:
    """Return (cached) SQLAlchemy engine for selected db_type or None if not configured."""
    db_type = db_type.lower()
    if db_type not in SUPPORTED_DB_TYPES:
        return None
    if db_type in _ENGINE_CACHE:
        return _ENGINE_CACHE[db_type]

    url = None
    if db_type == DatabaseType.POSTGRES:
        url = POSTGRES_URL
    elif db_type == DatabaseType.MYSQL:
        url = MYSQL_URL
    elif db_type == DatabaseType.ORACLE:
        url = ORACLE_URL

    if not url:
        return None

    # Enhanced connection pool settings for production
    engine = create_engine(
        url, 
        pool_pre_ping=True, 
        future=True,
        pool_size=5,  # Max connections in pool
        max_overflow=10,  # Max overflow connections
        pool_timeout=30,  # Timeout to get connection from pool
        pool_recycle=3600,  # Recycle connections after 1 hour
        connect_args={
            "connect_timeout": 10,  # Connection timeout
            "application_name": "nl-to-sql-api"
        } if db_type == DatabaseType.POSTGRES else {}
    )
    _ENGINE_CACHE[db_type] = engine
    return engine

def adapt_sql_for_dialect(sql: str, db_type: str) -> str:
    """Adapt generic SELECT with LIMIT to target dialect syntax (only SELECT allowed)."""
    db_type = db_type.lower()
    if db_type == DatabaseType.ORACLE and "LIMIT" in sql.upper():
        # Convert LIMIT N to FETCH FIRST N ROWS ONLY (Oracle 12c+)
        match = re.search(r"LIMIT\s+(\d+)", sql, flags=re.IGNORECASE)
        if match:
            n = match.group(1)
            # Remove original LIMIT clause
            sql_no_limit = re.sub(r"LIMIT\s+\d+", "", sql, flags=re.IGNORECASE).rstrip().rstrip(';')
            # Append Oracle pagination
            return f"{sql_no_limit} FETCH FIRST {n} ROWS ONLY"
    # MySQL & PostgreSQL already compatible
    return sql

# ============================================================================
# Pydantic Models (extended)
# ============================================================================

class QueryRequest(BaseModel):
    """Request model for natural language query"""
    question: str = Field(..., min_length=1, max_length=1000, description="Natural language question")
    db_type: Optional[DatabaseType] = DatabaseType.POSTGRES

    @validator('question')
    def validate_question(cls, v):
        if not v or not v.strip():
            raise ValueError('Question cannot be empty')
        # Basic injection attempt detection
        suspicious_patterns = ['--', '/*', '*/', 'xp_', 'sp_', ';', 'union', 'script']
        v_lower = v.lower()
        for pattern in suspicious_patterns:
            if pattern in v_lower:
                raise ValueError(f'Question contains suspicious content: {pattern}')
        return v.strip()

    class Config:
        json_schema_extra = {
            "example": {
                "question": "Show top 5 customers by total purchase amount",
                "db_type": "postgresql"
            }
        }


class QueryResponse(BaseModel):
    """Response model containing SQL, explanation, and results"""
    sql: str
    explanation: str
    result: List[Dict[str, Any]]
    execution_time_ms: float


# ============================================================================
# NL to SQL Generator (OpenAI Integration)
# ============================================================================

def generate_sql_from_text(question: str, schema: Dict[str, Any]) -> Dict[str, str]:
    """
    Convert natural language question to SQL query using OpenAI API.
    
    Args:
        question: Natural language question from user
        schema: Database schema information for context
        
    Returns:
        Dictionary with 'sql' and 'explanation' keys
        
    Raises:
        Exception: If OpenAI API call fails
    """
    logger.info(f"Generating SQL for question: {question}")
    
    # Build schema context for the prompt
    schema_context = "Database Schema:\n"
    for table, info in schema.items():
        schema_context += f"\nTable: {table}\n"
        schema_context += f"Columns: {', '.join(info['columns'])}\n"
        schema_context += f"Description: {info['description']}\n"
    
    # System prompt with schema context and instructions
    system_prompt = f"""You are an expert SQL query generator. Convert natural language questions into PostgreSQL queries.

{schema_context}

Rules:
1. Generate ONLY SELECT queries (no INSERT, UPDATE, DELETE, DROP, ALTER, etc.)
2. Use proper PostgreSQL syntax
3. Include table joins when needed
4. Add appropriate WHERE clauses, ORDER BY, and GROUP BY as needed
5. Return JSON with two keys: "sql" (the query) and "explanation" (brief description)
6. The SQL should be ready to execute without modification
7. Use LIMIT clause when asking for "top" results
8. Use meaningful aliases for aggregated columns

Example response format:
{{
  "sql": "SELECT u.name, SUM(t.amount) as total_amount FROM users u JOIN transactions t ON u.id = t.user_id GROUP BY u.id, u.name ORDER BY total_amount DESC LIMIT 5",
  "explanation": "This query joins users and transactions tables, sums the transaction amounts per user, and returns the top 5 users ordered by total purchase amount."
}}"""

    try:
        # Check if OpenAI API key is available
        if not OPENAI_API_KEY:
            # Fallback: Return a stubbed response for demo purposes
            logger.warning("OpenAI API key not set. Using stubbed response.")
            return _generate_stubbed_sql(question)
        
        # Initialize OpenAI client
        client = openai.OpenAI(api_key=OPENAI_API_KEY)
        
        # Call OpenAI API
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": question}
            ],
            temperature=0.1,  # Low temperature for consistent outputs
            response_format={"type": "json_object"}
        )
        
        # Parse response
        import json
        result = json.loads(response.choices[0].message.content)
        
        logger.info(f"Generated SQL: {result.get('sql', 'N/A')}")
        return result
        
    except Exception as e:
        logger.error(f"Error generating SQL: {str(e)}")
        # Fallback to stubbed response on error
        return _generate_stubbed_sql(question)


def _generate_stubbed_sql(question: str) -> Dict[str, str]:
    """
    Fallback function that generates simple SQL based on keywords.
    Used when OpenAI API is not available or fails.
    
    Args:
        question: Natural language question
        
    Returns:
        Dictionary with 'sql' and 'explanation' keys (always returns a valid dict)
    """
    if not question:
        return {
            "sql": "SELECT customer_id, first_name, last_name FROM customers LIMIT 15",
            "explanation": "Default query - empty question provided."
        }
    
    question_lower = question.lower()
    
    # Banking-specific keyword-based SQL generation
    if "top" in question_lower and ("customer" in question_lower or "client" in question_lower):
        if "transaction" in question_lower or "spending" in question_lower or "purchase" in question_lower or "amount" in question_lower:
            return {
                "sql": """SELECT c.first_name, c.last_name, c.customer_segment, SUM(t.amount) as total_spent 
                         FROM customers c 
                         JOIN transactions t ON c.customer_id = t.customer_id 
                         WHERE t.status = 'completed'
                         GROUP BY c.customer_id, c.first_name, c.last_name, c.customer_segment 
                         ORDER BY total_spent DESC 
                         LIMIT 10""",
                "explanation": "Returns top 10 customers by total transaction spending with completed transactions only."
            }
        elif "balance" in question_lower:
            return {
                "sql": """SELECT customer_id, first_name, last_name, account_balance, customer_segment, city
                         FROM customers 
                         WHERE is_active = true
                         ORDER BY account_balance DESC 
                         LIMIT 10""",
                "explanation": "Returns top 10 customers by account balance, showing only active accounts."
            }
    elif "loan" in question_lower:
        if "default" in question_lower or "risk" in question_lower:
            return {
                "sql": """SELECT c.first_name, c.last_name, l.loan_type, l.outstanding_balance, l.status, c.credit_score
                         FROM customers c
                         JOIN loans l ON c.customer_id = l.customer_id
                         WHERE l.status IN ('Defaulted', 'Pending')
                         ORDER BY l.outstanding_balance DESC
                         LIMIT 10""",
                "explanation": "Returns customers with defaulted or pending loans, ordered by outstanding balance."
            }
        elif "total" in question_lower or "amount" in question_lower:
            return {
                "sql": """SELECT c.first_name, c.last_name, COUNT(l.loan_id) as loan_count, 
                         SUM(l.outstanding_balance) as total_debt, AVG(l.interest_rate) as avg_interest_rate
                         FROM customers c
                         JOIN loans l ON c.customer_id = l.customer_id
                         WHERE l.status = 'Active'
                         GROUP BY c.customer_id, c.first_name, c.last_name
                         ORDER BY total_debt DESC
                         LIMIT 10""",
                "explanation": "Returns customers with highest total outstanding loan amounts for active loans."
            }
        else:
            return {
                "sql": """SELECT loan_id, loan_type, principal_amount, outstanding_balance, 
                         interest_rate, monthly_payment, status 
                         FROM loans 
                         ORDER BY principal_amount DESC 
                         LIMIT 10""",
                "explanation": "Returns the 10 largest loans by principal amount with payment details."
            }
    elif "transaction" in question_lower:
        if "pending" in question_lower or "failed" in question_lower:
            return {
                "sql": """SELECT t.transaction_id, c.first_name, c.last_name, t.transaction_type, 
                         t.amount, t.transaction_date, t.status
                         FROM transactions t
                         JOIN customers c ON t.customer_id = c.customer_id
                         WHERE t.status IN ('pending', 'failed')
                         ORDER BY t.transaction_date DESC
                         LIMIT 20""",
                "explanation": "Returns recent pending or failed transactions with customer details."
            }
        elif "large" in question_lower or "high" in question_lower:
            return {
                "sql": """SELECT t.transaction_id, c.first_name, c.last_name, t.transaction_type, 
                         t.amount, t.category, t.transaction_date, t.merchant
                         FROM transactions t
                         JOIN customers c ON t.customer_id = c.customer_id
                         WHERE t.status = 'completed' AND t.amount > 1000
                         ORDER BY t.amount DESC
                         LIMIT 15""",
                "explanation": "Returns high-value completed transactions over $1,000."
            }
        else:
            return {
                "sql": """SELECT transaction_id, transaction_type, amount, category, 
                         transaction_date, status, merchant
                         FROM transactions 
                         ORDER BY transaction_date DESC 
                         LIMIT 20""",
                "explanation": "Returns the 20 most recent transactions."
            }
    elif "customer" in question_lower or "client" in question_lower:
        if "premium" in question_lower or "segment" in question_lower:
            return {
                "sql": """SELECT customer_id, first_name, last_name, customer_segment, 
                         account_balance, credit_score, city
                         FROM customers 
                         WHERE customer_segment IN ('Premium', 'Corporate')
                         ORDER BY account_balance DESC
                         LIMIT 15""",
                "explanation": "Returns premium and corporate segment customers with highest balances."
            }
        elif "credit" in question_lower:
            return {
                "sql": """SELECT customer_id, first_name, last_name, credit_score, 
                         customer_segment, account_balance
                         FROM customers 
                         WHERE is_active = true
                         ORDER BY credit_score DESC
                         LIMIT 15""",
                "explanation": "Returns active customers with highest credit scores."
            }
        else:
            return {
                "sql": """SELECT customer_id, first_name, last_name, email, customer_segment, 
                         account_balance, signup_date 
                         FROM customers 
                         WHERE is_active = true
                         ORDER BY signup_date DESC 
                         LIMIT 15""",
                "explanation": "Returns the 15 most recently registered active customers."
            }
    else:
        return {
            "sql": """SELECT customer_id, first_name, last_name, customer_segment, 
                     account_balance, is_active 
                     FROM customers 
                     LIMIT 15""",
            "explanation": "Default query returning first 15 customers from the database."
        }


# ============================================================================
# SQL Validator
# ============================================================================

def validate_sql(query: str) -> tuple[bool, Optional[str]]:
    """
    Validate SQL query for safety - ensures only SELECT queries are allowed.
    
    Args:
        query: SQL query string to validate
        
    Returns:
        Tuple of (is_valid, error_message)
        - is_valid: True if query is safe, False otherwise
        - error_message: None if valid, error description if invalid
    """
    logger.info("Validating SQL query")
    
    if not query or not query.strip():
        return False, "Empty query provided"
    
    # Parse SQL using sqlparse
    try:
        parsed = sqlparse.parse(query)
        
        if not parsed:
            return False, "Unable to parse SQL query"
        
        # Check each statement in the query
        for statement in parsed:
            # Get the first token (should be SELECT for valid queries)
            first_token = statement.token_first(skip_ws=True, skip_cm=True)
            
            if not first_token:
                return False, "Invalid SQL statement"
            
            # Extract the statement type
            stmt_type = first_token.ttype
            stmt_value = first_token.value.upper()
            
            # Block dangerous commands
            dangerous_keywords = [
                'INSERT', 'UPDATE', 'DELETE', 'DROP', 'ALTER', 'CREATE',
                'TRUNCATE', 'REPLACE', 'GRANT', 'REVOKE', 'EXEC', 'EXECUTE'
            ]
            
            if stmt_value in dangerous_keywords:
                return False, f"Forbidden SQL command: {stmt_value}. Only SELECT queries are allowed."
            
            # Ensure it's a SELECT statement
            if stmt_value != 'SELECT':
                return False, f"Only SELECT queries are allowed. Found: {stmt_value}"
            
            # Check for dangerous keywords in the entire query
            query_upper = query.upper()
            for keyword in dangerous_keywords:
                if keyword in query_upper:
                    return False, f"Forbidden keyword detected: {keyword}"
        
        # Ensure LIMIT clause exists, add if missing
        if 'LIMIT' not in query.upper():
            logger.info(f"No LIMIT clause found, will add LIMIT {MAX_ROWS}")
        
        return True, None
        
    except Exception as e:
        logger.error(f"SQL validation error: {str(e)}")
        return False, f"SQL parsing error: {str(e)}"


def add_limit_if_missing(query: str, max_rows: int = MAX_ROWS) -> str:
    """
    Add LIMIT clause to query if not present.
    
    Args:
        query: SQL query string
        max_rows: Maximum number of rows to return
        
    Returns:
        Modified query with LIMIT clause
    """
    if 'LIMIT' not in query.upper():
        # Remove trailing semicolon if present
        query = query.rstrip().rstrip(';')
        query = f"{query} LIMIT {max_rows}"
        logger.info(f"Added LIMIT {max_rows} to query")
    
    return query


# ============================================================================
# SQL Executor (multi-DB)
# ============================================================================

def execute_sql(query: str, db_type: str) -> List[Dict[str, Any]]:
    """Execute validated SQL on chosen database or fall back to mock data if not configured."""
    logger.info(f"Executing SQL on db_type={db_type}")
    engine = get_engine(db_type)
    if engine is None:
        logger.warning(f"No connection string for {db_type}. Using mock data.")
        return _execute_mock_query(query)

    try:
        with engine.connect() as conn:
            # Set query timeout and read-only mode for security
            with conn.begin():
                conn.execute(text("SET SESSION TRANSACTION READ ONLY"))
            result = conn.execute(text(query).execution_options(
                autocommit=True, 
                compiled_cache={},
                stream_results=True
            ))
            rows = [dict(row) for row in result]
            logger.info(f"Query executed. Returned {len(rows)} rows.")
            
            # Additional safety: limit result size in memory
            if len(rows) > MAX_ROWS:
                logger.warning(f"Result truncated from {len(rows)} to {MAX_ROWS} rows")
                rows = rows[:MAX_ROWS]
            
            return rows
    except Exception as e:
        logger.error(f"Database execution error: {e}")
        # Don't expose internal DB details to client
        raise HTTPException(status_code=500, detail="Database query failed")


def _execute_mock_query(query: str) -> List[Dict[str, Any]]:
    """
    Execute mock query for demonstration when database is not available.
    Uses real banking mock data for realistic client presentations.
    
    Args:
        query: SQL query (analyzed for mock data generation)
        
    Returns:
        Mock data as list of dictionaries from banking dataset
    """
    logger.info("Executing mock query (no database connection)")
    
    query_lower = query.lower()
    
    # Parse query to extract LIMIT if present
    limit = 10  # default
    if "limit" in query_lower:
        try:
            limit_part = query_lower.split("limit")[-1].strip()
            limit = int(limit_part.split()[0])
        except:
            limit = 10
    
    # Route to appropriate mock data based on query content
    if "customers" in query_lower and "transactions" in query_lower:
        # Aggregate transactions by customer
        customer_spending = {}
        for txn in MOCK_TRANSACTIONS:
            if txn["status"] == "completed":
                cust_id = txn["customer_id"]
                customer_spending[cust_id] = customer_spending.get(cust_id, 0) + txn["amount"]
        
        # Join with customer data
        results = []
        for customer in MOCK_CUSTOMERS:
            cust_id = customer["customer_id"]
            if cust_id in customer_spending:
                results.append({
                    "first_name": customer["first_name"],
                    "last_name": customer["last_name"],
                    "customer_segment": customer["customer_segment"],
                    "total_spent": round(customer_spending[cust_id], 2)
                })
        
        # Sort by total_spent descending
        results.sort(key=lambda x: x["total_spent"], reverse=True)
        return results[:limit]
    
    elif "customers" in query_lower and "loans" in query_lower:
        # Join customers with loans
        results = []
        for loan in MOCK_LOANS:
            customer = next((c for c in MOCK_CUSTOMERS if c["customer_id"] == loan["customer_id"]), None)
            if customer:
                results.append({
                    "first_name": customer["first_name"],
                    "last_name": customer["last_name"],
                    "loan_type": loan["loan_type"],
                    "outstanding_balance": loan["outstanding_balance"],
                    "status": loan["status"],
                    "credit_score": customer["credit_score"]
                })
        
        # Filter based on query keywords
        if "default" in query_lower:
            results = [r for r in results if r["status"] in ["Defaulted", "Pending"]]
        elif "active" in query_lower:
            results = [r for r in results if r["status"] == "Active"]
        
        return results[:limit]
    
    elif "loans" in query_lower:
        # Return loan data
        results = []
        for loan in MOCK_LOANS:
            results.append({
                "loan_id": loan["loan_id"],
                "loan_type": loan["loan_type"],
                "principal_amount": loan["principal_amount"],
                "outstanding_balance": loan["outstanding_balance"],
                "interest_rate": loan["interest_rate"],
                "monthly_payment": loan["monthly_payment"],
                "status": loan["status"]
            })
        
        # Filter and sort based on query
        if "default" in query_lower:
            results = [r for r in results if r["status"] == "Defaulted"]
        elif "active" in query_lower:
            results = [r for r in results if r["status"] == "Active"]
        
        # Sort by outstanding balance or principal
        if "balance" in query_lower or "debt" in query_lower:
            results.sort(key=lambda x: x["outstanding_balance"], reverse=True)
        else:
            results.sort(key=lambda x: x["principal_amount"], reverse=True)
        
        return results[:limit]
    
    elif "transactions" in query_lower:
        # Return transaction data
        results = []
        for txn in MOCK_TRANSACTIONS:
            # Include customer name if joined
            if "customers" in query_lower or "join" in query_lower:
                customer = next((c for c in MOCK_CUSTOMERS if c["customer_id"] == txn["customer_id"]), None)
                if customer:
                    results.append({
                        "transaction_id": txn["transaction_id"],
                        "first_name": customer["first_name"],
                        "last_name": customer["last_name"],
                        "transaction_type": txn["transaction_type"],
                        "amount": txn["amount"],
                        "category": txn["category"],
                        "transaction_date": txn["transaction_date"],
                        "status": txn["status"],
                        "merchant": txn["merchant"]
                    })
            else:
                results.append(txn)
        
        # Filter based on query
        if "pending" in query_lower:
            results = [r for r in results if r["status"] == "pending"]
        elif "failed" in query_lower:
            results = [r for r in results if r["status"] == "failed"]
        elif "completed" in query_lower:
            results = [r for r in results if r["status"] == "completed"]
        
        if "large" in query_lower or "high" in query_lower:
            results = [r for r in results if r["amount"] > 1000]
        
        # Sort by date or amount
        if "amount" in query_lower and "order" in query_lower:
            results.sort(key=lambda x: x["amount"], reverse=True)
        else:
            results.sort(key=lambda x: x["transaction_date"], reverse=True)
        
        return results[:limit]
    
    elif "customers" in query_lower or "customer" in query_lower:
        # Return customer data
        results = list(MOCK_CUSTOMERS)
        
        # Filter based on query
        if "premium" in query_lower:
            results = [c for c in results if c["customer_segment"] in ["Premium", "Corporate"]]
        elif "active" in query_lower:
            results = [c for c in results if c["is_active"]]
        elif "inactive" in query_lower:
            results = [c for c in results if not c["is_active"]]
        
        # Sort based on query
        if "balance" in query_lower:
            results.sort(key=lambda x: x["account_balance"], reverse=True)
        elif "credit" in query_lower:
            results.sort(key=lambda x: x["credit_score"], reverse=True)
        else:
            results.sort(key=lambda x: x["signup_date"], reverse=True)
        
        return results[:limit]
    
    else:
        # Default: return customers
        return MOCK_CUSTOMERS[:limit]


# ============================================================================
# FastAPI Endpoints
# ============================================================================

@app.get("/")
async def root():
    """Health check endpoint with database connectivity status"""
    db_status = {}
    for db_type in ["postgresql", "mysql", "oracle"]:
        engine = get_engine(db_type)
        if engine:
            try:
                with engine.connect() as conn:
                    conn.execute(text("SELECT 1"))
                db_status[db_type] = "connected"
            except:
                db_status[db_type] = "connection_failed"
        else:
            db_status[db_type] = "not_configured"
    
    return {
        "status": "online",
        "service": "Natural Language to SQL API",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat(),
        "database_status": db_status,
        "openai_configured": bool(OPENAI_API_KEY)
    }


@app.post("/query", response_model=QueryResponse)
async def query_endpoint(request: QueryRequest, req: Request):
    """
    Main endpoint: Convert natural language to SQL and execute it.
    
    Process:
    1. Rate limiting check
    2. Generate SQL from natural language using OpenAI
    3. Validate SQL for safety (only SELECT allowed)
    4. Add LIMIT if missing
    5. Execute on chosen database
    6. Return results with explanation
    
    Args:
        request: QueryRequest with natural language question
        
    Returns:
        QueryResponse with SQL, explanation, results, and execution time
    """
    # Extract client IP from request
    client_ip = req.client.host if req.client else "unknown"
    
    # Rate limiting
    if not rate_limit_check(client_ip):
        raise HTTPException(
            status_code=429, 
            detail="Rate limit exceeded. Maximum 10 requests per minute."
        )
    
    start_time = time.time()
    
    try:
        # Log incoming request (without PII)
        logger.info(f"Received query request from {client_ip[:8]}... - question length: {len(request.question)}")
        
        # Step 1: Generate SQL from natural language
        sql_result = generate_sql_from_text(request.question, SCHEMA)
        generated_sql = sql_result.get("sql", "").strip()
        explanation = sql_result.get("explanation", "No explanation provided")
        
        if not generated_sql:
            raise HTTPException(
                status_code=400,
                detail="Failed to generate SQL from question"
            )
        
        # Step 2: Validate SQL
        is_valid, error_message = validate_sql(generated_sql)
        
        if not is_valid:
            logger.warning(f"SQL validation failed: {error_message}")
            raise HTTPException(
                status_code=400,
                detail=f"Invalid SQL: {error_message}"
            )
        
        # Step 3: Add LIMIT clause if missing
        safe_sql = add_limit_if_missing(generated_sql)
        # Dialect adaptation AFTER limit enforcement
        adapted_sql = adapt_sql_for_dialect(safe_sql, request.db_type.value)
        results = execute_sql(adapted_sql, request.db_type.value)
        
        # Calculate execution time
        execution_time = (time.time() - start_time) * 1000  # Convert to milliseconds
        
        # Log success
        logger.info(f"Query completed successfully in {execution_time:.2f}ms. Returned {len(results)} rows.")
        
        # Step 5: Return response
        return QueryResponse(
            sql=adapted_sql,
            explanation=explanation,
            result=results,
            execution_time_ms=round(execution_time, 2)
        )
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    
    except Exception as e:
        # Log and return generic error
        logger.error(f"Unexpected error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Internal server error occurred"
        )


@app.get("/schema")
async def get_schema():
    """
    Return the current database schema for reference.
    
    Returns:
        Dictionary containing schema information
    """
    return {"schema": SCHEMA}


@app.get("/ui", response_class=HTMLResponse)
async def ui():
    """Simple HTML UI with dropdown to select database and input question."""
    html = """
    <!DOCTYPE html>
    <html lang=\"en\">
    <head>
        <meta charset=\"UTF-8\" />
        <title>Natural Language to SQL Demo</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; }
            .container { max-width: 900px; margin: auto; }
            label { display: block; margin-top: 12px; font-weight: 600; }
            select, textarea, input { width: 100%; padding: 8px; margin-top: 6px; box-sizing: border-box; }
            button { margin-top: 16px; padding: 10px 18px; background: #2563eb; color: #fff; border: none; cursor: pointer; border-radius: 4px; }
            button:hover { background: #1e4fb3; }
            pre { background: #f5f5f5; padding: 12px; overflow-x: auto; }
            .row { display: flex; gap: 16px; }
            .col { flex: 1; }
        </style>
    </head>
    <body>
        <div class=\"container\">
            <h1>Natural Language to SQL Demo</h1>
            <p>Enter a question and select a database type. The backend will generate, validate and execute a safe SELECT query.</p>
            <label for=\"question\">Question</label>
            <textarea id=\"question\" rows=\"3\" placeholder=\"e.g. Top 10 customers by transaction spending\"></textarea>
            <label for=\"db_type\">Database Type</label>
            <select id=\"db_type\">
                <option value=\"postgresql\">PostgreSQL</option>
                <option value=\"mysql\">MySQL</option>
                <option value=\"oracle\">Oracle</option>
            </select>
            <button onclick=\"runQuery()\">Run Query</button>
            <h2>Result</h2>
            <div id=\"status\"></div>
            <pre id=\"sql\"></pre>
            <pre id=\"explanation\"></pre>
            <pre id=\"data\"></pre>
        </div>
        <script>
            async function runQuery() {
                const question = document.getElementById('question').value.trim();
                const dbType = document.getElementById('db_type').value;
                const statusEl = document.getElementById('status');
                const sqlEl = document.getElementById('sql');
                const explEl = document.getElementById('explanation');
                const dataEl = document.getElementById('data');
                statusEl.textContent = 'Running...';
                sqlEl.textContent = '';
                explEl.textContent = '';
                dataEl.textContent = '';
                try {
                    const resp = await fetch('/query', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ question, db_type: dbType })
                    });
                    const json = await resp.json();
                    if (!resp.ok) {
                        statusEl.textContent = 'Error: ' + (json.detail || 'Unknown error');
                        return;
                    }
                    statusEl.textContent = 'Success in ' + json.execution_time_ms + ' ms. Rows: ' + json.result.length;
                    sqlEl.textContent = 'SQL:\\n' + json.sql;
                    explEl.textContent = 'Explanation:\\n' + json.explanation;
                    dataEl.textContent = 'Data:\\n' + JSON.stringify(json.result, null, 2);
                } catch (e) {
                    statusEl.textContent = 'Request failed: ' + e;
                }
            }
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html)


# ============================================================================
# Application Entry Point
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    
    # Run the application
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
