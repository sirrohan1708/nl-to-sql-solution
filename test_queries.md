# NL to SQL Test Queries

This file contains various test queries to validate the Natural Language to SQL API functionality.

## Server Endpoints

- **Main UI**: http://localhost:8000/ui
- **API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/
- **Schema**: http://localhost:8000/schema

## Test Categories

### 1. Basic Customer Queries

#### Simple Customer List
**Question**: "Show me all customers"
**Expected**: Basic customer listing with default limit

#### Active Customers
**Question**: "Show active customers"
**Expected**: Only customers where is_active = true

#### Premium Customers
**Question**: "Show premium customers"
**Expected**: Customers with Premium or Corporate segments

### 2. Transaction Analysis

#### Top Spending Customers
**Question**: "Top 10 customers by transaction spending"
**Expected**: JOIN customers + transactions, SUM amounts, ORDER BY DESC

#### Recent Transactions
**Question**: "Show recent transactions"
**Expected**: Latest transactions ordered by date

#### High Value Transactions
**Question**: "Show large transactions"
**Expected**: Transactions > $1000, filtered by amount

#### Failed Transactions
**Question**: "Show failed or pending transactions"
**Expected**: Transactions with status 'failed' or 'pending'

### 3. Loan Queries

#### Default Risk Analysis
**Question**: "Show customers with defaulted loans"
**Expected**: JOIN customers + loans, filter by 'Defaulted' status

#### Loan Portfolio
**Question**: "Show total loan amounts by customer"
**Expected**: SUM outstanding balances grouped by customer

#### Active Loans
**Question**: "Show active loans"
**Expected**: Loans with 'Active' status

### 4. Credit Analysis

#### High Credit Score Customers
**Question**: "Show customers with highest credit scores"
**Expected**: ORDER BY credit_score DESC

#### Credit Risk by Balance
**Question**: "Show customer balances and credit scores"
**Expected**: Account balance vs credit score analysis

### 5. Database Type Testing

Test the same query across different database types:

#### PostgreSQL Test
**Question**: "Top 5 customers by spending"
**Database**: postgresql
**Expected**: Standard SQL with LIMIT

#### MySQL Test  
**Question**: "Top 5 customers by spending"
**Database**: mysql
**Expected**: Standard SQL with LIMIT

#### Oracle Test
**Question**: "Top 5 customers by spending" 
**Database**: oracle
**Expected**: SQL with FETCH FIRST N ROWS ONLY

### 6. Edge Cases & Validation

#### Empty Query
**Question**: ""
**Expected**: Validation error

#### SQL Injection Attempts (Should Fail)
**Question**: "Show customers; DROP TABLE customers;"
**Expected**: Validation error - forbidden keywords

**Question**: "Show customers UNION SELECT * FROM users"
**Expected**: Validation error - suspicious content

#### Long Query
**Question**: "Show me detailed information about all premium customers including their transaction history and loan details with full contact information and account balances"
**Expected**: Should work (under 1000 char limit)

### 7. Performance Testing

#### Large Result Set
**Question**: "Show all transactions"
**Expected**: Results limited to MAX_ROWS (1000)

#### Complex Aggregation
**Question**: "Show average transaction amount by customer segment"
**Expected**: Complex GROUP BY with aggregations

### 8. Curl Commands for API Testing

```bash
# Basic customer query
curl -X POST "http://localhost:8000/query" \
     -H "Content-Type: application/json" \
     -d '{"question": "Show top 5 customers by transaction spending", "db_type": "postgresql"}'

# Oracle dialect test
curl -X POST "http://localhost:8000/query" \
     -H "Content-Type: application/json" \
     -d '{"question": "Show top 5 customers by transaction spending", "db_type": "oracle"}'

# Health check
curl -X GET "http://localhost:8000/"

# Schema information
curl -X GET "http://localhost:8000/schema"

# Rate limit test (run multiple times quickly)
for i in {1..15}; do
  curl -X POST "http://localhost:8000/query" \
       -H "Content-Type: application/json" \
       -d '{"question": "Show customers", "db_type": "postgresql"}'
done
```

### 9. Expected Mock Data Responses

Since no real database is configured, all queries will return mock banking data:

- **Customers**: 100 mock customer records
- **Transactions**: 300+ mock transaction records  
- **Loans**: 80+ mock loan records

The mock data includes realistic banking fields like:
- Customer segments (Premium, Retail, Corporate)
- Transaction types (purchase, transfer, deposit)
- Loan types (Mortgage, Auto, Personal, Business)
- Transaction statuses (completed, pending, failed)

### 10. Testing Checklist

- [x] Web UI loads at /ui
- [x] Swagger docs accessible at /docs  
- [x] Health endpoint shows database status
- [x] Basic customer queries work
- [x] Transaction analysis queries work
- [x] Loan queries work
- [x] All three database types work (postgresql, mysql, oracle)
- [x] Oracle queries use FETCH FIRST instead of LIMIT
- [x] Rate limiting kicks in after 10 requests
- [x] SQL injection attempts are blocked
- [x] Empty/invalid queries return proper errors
- [x] Results are limited to MAX_ROWS
- [x] Response times are logged
- [x] Mock data is returned when no DB configured

### 11. Browser Testing Steps

1. Go to http://localhost:8000/ui
2. Try each test question from above
3. Switch between database types
4. Verify SQL generation is different for Oracle
5. Check that results are displayed properly
6. Test rate limiting by submitting quickly
7. Try edge cases and validate error handling

### 12. Performance Expectations

- **Response Time**: < 200ms for mock data queries
- **Rate Limit**: 10 requests/minute per IP
- **Memory Usage**: Results truncated at 1000 rows max
- **SQL Generation**: Fallback to keyword-based when OpenAI not configured
