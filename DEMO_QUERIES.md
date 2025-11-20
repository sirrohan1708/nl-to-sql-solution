# Banking NL to SQL - Quick Demo Queries
# =======================================

# Example Natural Language Questions for Banking Client Demo
# Use these with: curl -X POST "http://localhost:8000/query" -H "Content-Type: application/json" -d '{"question": "YOUR_QUESTION_HERE"}'

## Customer Analytics
1. "Show me the top 10 customers by total spending"
2. "Show me premium customers with highest account balances"
3. "Show me customers with highest credit scores"
4. "Show me recently registered active customers"
5. "Show me all corporate segment customers"

## Transaction Analysis
6. "Show me all large transactions above $1000"
7. "Show me all pending transactions"
8. "Show me all failed transactions"
9. "Show me recent completed transactions"
10. "Show me transactions by category"

## Loan & Risk Management
11. "Show me customers with defaulted loans"
12. "Show me the largest active loans"
13. "Show me customers with highest total debt"
14. "Show me all mortgage loans"
15. "Show me high-risk pending loans"

## Business Intelligence
16. "Show me customers by city"
17. "Show me account balance distribution"
18. "Show me transaction trends by type"
19. "Show me loan performance by type"
20. "Show me customer growth by segment"

## Key Features to Highlight During Demo:
- ✅ 100 realistic customer records
- ✅ 500+ banking transactions (deposits, withdrawals, transfers)
- ✅ 100+ loan records (mortgages, auto, personal, business)
- ✅ Real-time SQL generation from natural language
- ✅ Automatic security validation (only SELECT queries)
- ✅ Immediate results with execution time
- ✅ Works without database setup (mock mode)

## Demo Flow Suggestion:
1. Start with simple query: "Show me customers"
2. Progress to joins: "Show me top customers by spending"
3. Show filtering: "Show me defaulted loans"
4. Demonstrate security: Try "DELETE FROM customers" (will be blocked)
5. Show performance: Note execution times in milliseconds
6. Show schema: http://localhost:8000/schema

## For Interactive API Testing:
Visit: http://localhost:8000/docs

## Quick PowerShell Demo Commands:

# Top customers by spending
curl.exe -X POST "http://localhost:8000/query" -H "Content-Type: application/json" -d '{\"question\": \"Show me top 10 customers by total spending\"}'

# High-value transactions
curl.exe -X POST "http://localhost:8000/query" -H "Content-Type: application/json" -d '{\"question\": \"Show me large transactions above 1000 dollars\"}'

# Loan risk analysis
curl.exe -X POST "http://localhost:8000/query" -H "Content-Type: application/json" -d '{\"question\": \"Show me customers with defaulted loans\"}'

# Premium customers
curl.exe -X POST "http://localhost:8000/query" -H "Content-Type: application/json" -d '{\"question\": \"Show me premium customers by balance\"}'

# Pending transactions
curl.exe -X POST "http://localhost:8000/query" -H "Content-Type: application/json" -d '{\"question\": \"Show me pending transactions\"}'
