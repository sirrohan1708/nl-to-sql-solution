# Natural Language to SQL Prototype

A production-ready FastAPI application that converts natural language questions into SQL queries, validates them for safety, and executes them on a PostgreSQL database (read-only mode).

## Features

- 🤖 **AI-Powered**: Uses OpenAI GPT-4 to convert natural language to SQL
- 🔒 **Secure**: Validates all queries to ensure only SELECT statements are executed
- ⚡ **Fast**: Built with FastAPI for high performance
- 📊 **Database Ready**: PostgreSQL integration with connection pooling
- 🎯 **Limited**: Automatic LIMIT clause addition and row/time constraints
- 📝 **Logged**: Complete audit trail of all queries and execution times
- 🔄 **Mock Mode**: Works without database/OpenAI for testing

## Architecture

```
┌─────────────┐
│   Client    │
└──────┬──────┘
       │ POST /query
       │ {"question": "..."}
       ▼
┌─────────────────────────────┐
│      FastAPI Server         │
├─────────────────────────────┤
│  1. NL Parser (OpenAI)      │
│     └─> Generate SQL        │
│  2. Validator (sqlparse)    │
│     └─> Check safety        │
│  3. Executor (psycopg2)     │
│     └─> Run query           │
└──────┬──────────────────────┘
       │ {"sql": "...", "result": [...]}
       ▼
┌─────────────┐
│  Response   │
└─────────────┘
```

## Installation

### Prerequisites
- Python 3.9 or higher
- PostgreSQL database (optional for testing)
- OpenAI API key (optional for testing)

### Setup Steps

1. **Clone or navigate to the project directory**
   ```powershell
   cd c:\Users\r.vijay.sirsulwar\Videos\nl_to_sql_solution
   ```

2. **Create a virtual environment** (recommended)
   ```powershell
   python -m venv venv
   .\venv\Scripts\Activate.ps1
   ```

3. **Install dependencies**
   ```powershell
   pip install -r requirements.txt
   ```

4. **Configure environment variables**
   ```powershell
   # Copy the example file
   copy .env.example .env
   
   # Edit .env and add your credentials
   # - OPENAI_API_KEY: Your OpenAI API key
   # - DATABASE_URL: Your PostgreSQL connection string
   ```

5. **Run the application**
   ```powershell
   uvicorn main:app --reload
   ```

   The server will start at `http://localhost:8000`

## Usage

### API Endpoints

#### 1. Query Endpoint (Main)
**POST** `/query`

Convert natural language to SQL and execute it.

**Request:**
```json
{
  "question": "Show top 5 customers by total purchase amount"
}
```

**Response:**
```json
{
  "sql": "SELECT u.name, SUM(t.amount) as total_amount FROM users u JOIN transactions t ON u.id = t.user_id GROUP BY u.id, u.name ORDER BY total_amount DESC LIMIT 5",
  "explanation": "This query joins users and transactions tables, sums amounts per user, and returns top 5 by total purchase amount.",
  "result": [
    {"name": "Alice Johnson", "total_amount": 15420.50},
    {"name": "Bob Smith", "total_amount": 12890.25}
  ],
  "execution_time_ms": 45.23
}
```

#### 2. Schema Endpoint
**GET** `/schema`

Returns the current database schema.

#### 3. Health Check
**GET** `/`

Returns API status and version.

### Example Requests

#### Using cURL (PowerShell)
```powershell
# Query for top customers by spending
curl.exe -X POST "http://localhost:8000/query" `
  -H "Content-Type: application/json" `
  -d '{\"question\": \"Show me top 10 customers by total spending\"}'

# Get high-value transactions
curl.exe -X POST "http://localhost:8000/query" `
  -H "Content-Type: application/json" `
  -d '{\"question\": \"Show me large transactions above 1000 dollars\"}'

# Analyze loan risk
curl.exe -X POST "http://localhost:8000/query" `
  -H "Content-Type: application/json" `
  -d '{\"question\": \"Show me customers with defaulted loans\"}'

# Get schema
curl.exe -X GET "http://localhost:8000/schema"
```

#### Interactive Demo Script (PowerShell)
For a complete client presentation with 8 pre-configured queries:
```powershell
.\demo_banking_queries.ps1
```

See `DEMO_QUERIES.md` for 20+ example questions and `PRESENTATION_GUIDE.md` for a complete presentation walkthrough.

#### Using Python
```python
import requests

response = requests.post(
    "http://localhost:8000/query",
    json={"question": "Top 5 users by transaction amount"}
)

result = response.json()
print(f"SQL: {result['sql']}")
print(f"Results: {result['result']}")
```

## Database Schema

The prototype includes realistic banking data with three tables:

### `customers` Table (100 records)
- `customer_id` - Unique customer identifier
- `first_name`, `last_name` - Customer name
- `email`, `phone` - Contact information
- `city`, `state` - Location
- `account_type` - Savings, Checking, Premium, Business, Student
- `customer_segment` - Retail, Premium, Corporate, Business, Student
- `credit_score` - 600-850 range
- `signup_date` - Account opening date
- `account_balance` - Current balance ($500 - $250,000)
- `is_active` - Account status

### `transactions` Table (~1,000 records)
- `transaction_id` - Unique transaction identifier
- `customer_id` - Foreign key to customers
- `transaction_type` - ATM Withdrawal, Deposit, Wire Transfer, etc.
- `category` - Groceries, Utilities, Salary, etc.
- `amount` - Transaction amount
- `currency` - Currency code (USD, EUR, GBP)
- `transaction_date`, `transaction_time` - When transaction occurred
- `status` - completed, pending, failed
- `merchant`, `location` - Transaction details
- `description` - Transaction description

### `loans` Table (~120 records)
- `loan_id` - Unique loan identifier
- `customer_id` - Foreign key to customers
- `loan_type` - Personal, Home Mortgage, Auto, Business, Student, Credit Card
- `principal_amount` - Original loan amount
- `outstanding_balance` - Remaining balance
- `interest_rate` - Annual percentage rate
- `term_months` - Loan term length
- `monthly_payment` - Required monthly payment
- `start_date` - Loan origination date
- `status` - Active, Paid Off, Defaulted, Pending
- `credit_score_at_approval` - Credit score when loan was approved

## Security Features

### SQL Validation
- ✅ Only `SELECT` statements allowed
- ❌ Blocks: INSERT, UPDATE, DELETE, DROP, ALTER, CREATE, TRUNCATE, etc.
- 🔍 Uses `sqlparse` for proper SQL parsing
- 🎯 Auto-adds `LIMIT` clause if missing (max 1000 rows)

### Database Safety
- Read-only database user recommended
- Query timeout: 30 seconds
- Maximum rows: 1000
- Connection timeout: 10 seconds

### Error Handling
- All errors logged with timestamps
- User-friendly error messages
- No sensitive data exposed in errors

## Configuration

### Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `OPENAI_API_KEY` | OpenAI API key for NL parsing | `sk-...` |
| `DATABASE_URL` | PostgreSQL connection string | `postgresql://user:pass@localhost:5432/db` |

### Constants (in `main.py`)

| Constant | Default | Description |
|----------|---------|-------------|
| `MAX_ROWS` | 1000 | Maximum rows returned |
| `QUERY_TIMEOUT` | 30 | Query timeout in seconds |

## Mock Mode

The application works without database or OpenAI configuration:

- **No OpenAI Key**: Uses keyword-based SQL generation
- **No Database**: Returns realistic mock data

This allows for testing and development without external dependencies.

## Development

### Project Structure
```
nl_to_sql_solution/
├── main.py              # Main application file
├── requirements.txt     # Python dependencies
├── .env                 # Environment variables (create from .env.example)
├── .env.example         # Environment template
├── README.md            # This file
└── .github/
    └── copilot-instructions.md  # Copilot configuration
```

### Testing

Test the application with various queries:

```powershell
# Valid queries
curl.exe -X POST "http://localhost:8000/query" -H "Content-Type: application/json" -d '{\"question\": \"Show all users\"}'

# Complex queries
curl.exe -X POST "http://localhost:8000/query" -H "Content-Type: application/json" -d '{\"question\": \"Average transaction amount by city\"}'
```

### Logs

All operations are logged to console with timestamps:
- Incoming requests
- Generated SQL
- Validation results
- Execution time
- Errors

## Production Considerations

Before deploying to production:

1. **Database Setup**
   - Create a read-only database user
   - Grant only SELECT permissions
   - Use connection pooling

2. **Security**
   - Store credentials securely (not in .env)
   - Use HTTPS
   - Add authentication/authorization
   - Rate limiting

3. **Monitoring**
   - Add metrics collection
   - Set up error alerting
   - Monitor query performance

4. **Scaling**
   - Add caching layer
   - Use async database driver
   - Deploy with Gunicorn + Nginx

## Troubleshooting

### Common Issues

**Issue**: `ModuleNotFoundError: No module named 'fastapi'`
- **Solution**: Install dependencies: `pip install -r requirements.txt`

**Issue**: `openai.error.AuthenticationError`
- **Solution**: Check your OpenAI API key in `.env`

**Issue**: `psycopg2.OperationalError`
- **Solution**: Verify DATABASE_URL format and database is running

**Issue**: Application runs but returns mock data
- **Solution**: This is expected behavior when DATABASE_URL is not set

## License

MIT License - feel free to use this for learning and development.

## Support

For issues or questions:
1. Check the logs for detailed error messages
2. Verify environment variables are set correctly
3. Test with mock mode first (no external dependencies)
4. Review the inline code comments for implementation details
