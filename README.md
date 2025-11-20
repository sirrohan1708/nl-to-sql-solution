# Natural Language to SQL API

[![Python](https://img.shields.io/badge/python-v3.12+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104.1-green.svg)](https://fastapi.tiangolo.com/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

A production-ready FastAPI application that converts natural language questions into SQL queries, validates them for safety, and executes them on multiple database types with comprehensive security features.

## 🚀 **Features**

### Core Functionality
- **Natural Language Processing**: Convert plain English questions to SQL using OpenAI GPT-4
- **Multi-Database Support**: PostgreSQL, MySQL, and Oracle with dialect-specific SQL generation
- **Mock Banking Data**: Realistic banking dataset for testing and demonstrations (100 customers, 1000+ transactions, 120+ loans)
- **Real-time Execution**: Execute queries with timeout protection and result limiting

### Security & Production Features
- **SQL Injection Protection**: Comprehensive validation preventing dangerous SQL commands
- **Rate Limiting**: 10 requests per minute per IP address with automatic cleanup
- **Input Validation**: Pydantic models with pattern detection for malicious content
- **CORS & Security Middleware**: Production-ready security headers and CORS policies
- **Read-Only Transactions**: Database queries execute in read-only mode for safety

### Monitoring & Reliability
- **Health Checks**: Database connectivity monitoring and system status
- **Structured Logging**: Request tracking with IP anonymization for security
- **Connection Pooling**: Optimized SQLAlchemy connections with proper timeout handling
- **Error Handling**: Generic error responses to prevent information disclosure

## 📋 **Requirements**

### System Requirements
- **Python 3.12+** (tested with Python 3.12.0)
- **Windows/Linux/macOS** (tested on Windows)
- **Memory**: Minimum 512MB RAM
- **Disk Space**: ~500MB for dependencies and mock data

### Python Dependencies
```
fastapi==0.104.1           # Web framework
uvicorn[standard]==0.24.0  # ASGI server
pydantic==2.5.0           # Data validation
sqlparse==0.4.4           # SQL parsing and validation
sqlalchemy==2.0.44        # Database ORM
openai==1.3.7             # OpenAI API integration
python-dotenv==1.0.0      # Environment variables
python-multipart==0.0.6   # Form data handling

# Database drivers
psycopg2-binary==2.9.9    # PostgreSQL
mysqlclient==2.2.7        # MySQL
oracledb==3.4.1           # Oracle

# Security packages (optional)
python-jose[cryptography]==3.3.0  # JWT handling
passlib[bcrypt]==1.7.4            # Password hashing
```

### Optional Dependencies
- **OpenAI API Key**: For advanced natural language processing (falls back to keyword-based SQL generation)
- **Database Connections**: PostgreSQL, MySQL, or Oracle (uses mock data if not configured)

## 🏗 **Architecture**

### Component Architecture
```
┌─────────────────────┐    ┌──────────────────────┐    ┌─────────────────────┐
│   Web UI / API      │    │   Security Layer     │    │   Database Layer    │
│                     │    │                      │    │                     │
│ • FastAPI Routes    │───▶│ • Rate Limiting      │───▶│ • PostgreSQL       │
│ • Request Validation│    │ • SQL Injection      │    │ • MySQL             │
│ • Response Formatting│   │ • Input Sanitization │    │ • Oracle            │
└─────────────────────┘    └──────────────────────┘    └─────────────────────┘
           │                           │                           │
           ▼                           ▼                           ▼
┌─────────────────────┐    ┌──────────────────────┐    ┌─────────────────────┐
│   NL Processing     │    │   SQL Generation     │    │   Mock Data Fallback│
│                     │    │                      │    │                     │
│ • OpenAI GPT-4      │───▶│ • Dialect Adaptation │    │ • Banking Dataset   │
│ • Keyword Fallback  │    │ • Query Validation   │    │ • 1000+ Records     │
│ • Context Injection │    │ • Limit Enforcement  │    │ • Realistic Fields  │
└─────────────────────┘    └──────────────────────┘    └─────────────────────┘
```

### Security Architecture
- **Input Layer**: Pydantic validation with pattern detection
- **Processing Layer**: SQL parsing and dangerous keyword blocking  
- **Execution Layer**: Read-only transactions with timeout protection
- **Output Layer**: Generic error messages and result size limiting

## 🛠 **Installation & Setup**

### 1. Clone the Repository
```bash
git clone https://github.com/sirrohan1708/nl-to-sql-solution.git
cd nl-to-sql-solution
```

### 2. Install Python Dependencies
```bash
# Using pip
pip install -r requirements.txt

# Or using Windows Python launcher
py -m pip install -r requirements.txt

# Windows with full Python path (if Python not in PATH)
& "$env:LOCALAPPDATA\Programs\Python\Python312\python.exe" -m pip install -r requirements.txt
```

### 3. Environment Configuration (Optional)
Create a `.env` file in the project root:
```env
# OpenAI Configuration (optional - uses keyword fallback if not provided)
OPENAI_API_KEY=your_openai_api_key_here

# Database Connections (optional - uses mock data if not provided)
POSTGRES_URL=postgresql://username:password@localhost:5432/dbname
MYSQL_URL=mysql://username:password@localhost:3306/dbname
ORACLE_URL=oracle+cx_oracle://username:password@localhost:1521/?service_name=XE

# Legacy compatibility
DATABASE_URL=postgresql://username:password@localhost:5432/dbname
```

### 4. Run the Application
```bash
# Standard startup
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Windows with full Python path
& "$env:LOCALAPPDATA\Programs\Python\Python312\python.exe" -m uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Production startup (without auto-reload)
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

## 🌐 **API Endpoints**

### Core Endpoints
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/ui` | GET | Interactive web interface for testing |
| `/docs` | GET | OpenAPI/Swagger documentation |
| `/query` | POST | Main NL to SQL conversion endpoint |
| `/` | GET | Health check and system status |
| `/schema` | GET | Database schema information |

### Query Endpoint Usage
```bash
# PowerShell example
$body = @{
    question = "Top 10 customers by transaction spending"
    db_type = "postgresql"
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:8000/query" -Method POST -Body $body -ContentType "application/json"

# cURL example (Linux/macOS)
curl -X POST "http://localhost:8000/query" \
     -H "Content-Type: application/json" \
     -d '{"question": "Show top 5 customers by spending", "db_type": "postgresql"}'
```

### Sample API Response
```json
{
  "sql": "SELECT c.first_name, c.last_name, c.customer_segment, SUM(t.amount) as total_spent FROM customers c JOIN transactions t ON c.customer_id = t.customer_id WHERE t.status = 'completed' GROUP BY c.customer_id, c.first_name, c.last_name, c.customer_segment ORDER BY total_spent DESC LIMIT 10",
  "explanation": "Returns top 10 customers by total transaction spending with completed transactions only.",
  "result": [
    {
      "first_name": "Raymond",
      "last_name": "Watson", 
      "customer_segment": "Retail",
      "total_spent": 48949.74
    }
  ],
  "execution_time_ms": 5.08
}
```

## 🧪 **Testing & Validation**

### Quick Start Testing
1. **Open Web UI**: Navigate to http://localhost:8000/ui
2. **Try Sample Queries**:
   - "Show me all customers"
   - "Top 10 customers by transaction spending"
   - "Show customers with defaulted loans"
3. **Test Database Types**: Switch between PostgreSQL, MySQL, and Oracle
4. **Security Testing**: Try "Show customers; DROP TABLE customers;" (should be blocked)

### Comprehensive Test Suite
The `test_queries.md` file contains 50+ test scenarios covering:
- ✅ Basic customer queries
- ✅ Complex transaction analysis
- ✅ Loan portfolio queries  
- ✅ Multi-database dialect testing
- ✅ Security validation (SQL injection prevention)
- ✅ Rate limiting and performance testing
- ✅ Edge cases and error handling

### Performance Benchmarks
- **Query Response Time**: < 200ms for mock data
- **Rate Limit**: 10 requests/minute per IP
- **Memory Usage**: Results limited to 1000 rows max
- **Concurrent Users**: Supports 50+ concurrent connections

## 📊 **Mock Banking Dataset**

### Data Overview
- **100 Customers**: Diverse customer segments (Premium, Retail, Corporate, Student)
- **1000+ Transactions**: Multiple transaction types across all customers
- **120+ Loans**: Various loan types (Mortgage, Auto, Personal, Business)

### Schema Design
```sql
-- Customers table
customers (
    customer_id, first_name, last_name, email, phone,
    city, state, account_type, customer_segment, credit_score,
    signup_date, account_balance, is_active
)

-- Transactions table  
transactions (
    transaction_id, customer_id, transaction_type, category,
    amount, currency, transaction_date, transaction_time,
    status, merchant, location, description
)

-- Loans table
loans (
    loan_id, customer_id, loan_type, principal_amount,
    outstanding_balance, interest_rate, term_months,
    monthly_payment, start_date, status, credit_score_at_approval
)
```

### Sample Auto-Generated Queries
```sql
-- Top customers by spending (auto-generated from "Top 10 customers by transaction spending")
SELECT c.first_name, c.last_name, c.customer_segment, SUM(t.amount) as total_spent 
FROM customers c 
JOIN transactions t ON c.customer_id = t.customer_id 
WHERE t.status = 'completed'
GROUP BY c.customer_id, c.first_name, c.last_name, c.customer_segment 
ORDER BY total_spent DESC 
LIMIT 10

-- Risk analysis (auto-generated from "Show customers with defaulted loans")
SELECT c.first_name, c.last_name, l.loan_type, l.outstanding_balance, l.status, c.credit_score
FROM customers c
JOIN loans l ON c.customer_id = l.customer_id
WHERE l.status IN ('Defaulted', 'Pending')
ORDER BY l.outstanding_balance DESC
```

## 🔧 **Database Dialect Support**

The application automatically adapts SQL syntax for different databases:

**PostgreSQL/MySQL**:
```sql
SELECT * FROM customers ORDER BY signup_date DESC LIMIT 10
```

**Oracle**:
```sql  
SELECT * FROM customers ORDER BY signup_date DESC FETCH FIRST 10 ROWS ONLY
```

### Configuration Options
| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `OPENAI_API_KEY` | OpenAI API key for advanced NL processing | None | No |
| `POSTGRES_URL` | PostgreSQL connection string | None | No |
| `MYSQL_URL` | MySQL connection string | None | No |
| `ORACLE_URL` | Oracle connection string | None | No |
| `DATABASE_URL` | Legacy PostgreSQL connection | None | No |

### Application Settings
```python
# Performance settings
MAX_ROWS = 1000           # Maximum result rows
QUERY_TIMEOUT = 30        # Query timeout in seconds
RATE_LIMIT = 10          # Requests per minute per IP

# Connection pool settings
POOL_SIZE = 5            # Base connection pool size
MAX_OVERFLOW = 10        # Additional overflow connections
POOL_TIMEOUT = 30        # Connection acquisition timeout
POOL_RECYCLE = 3600      # Connection recycling interval
```

## 🔒 **Security Features**

### Input Validation
- **SQL Injection Prevention**: Comprehensive SQL parsing and validation
- **Pattern Detection**: Block suspicious patterns like `--`, `/*`, `union`, etc.
- **Query Length Limits**: Maximum 1000 characters per question
- **Keyword Blacklisting**: Block dangerous SQL commands (DROP, INSERT, DELETE, etc.)

### Rate Limiting & Access Control  
- **IP-based Rate Limiting**: 10 requests per minute per IP address
- **Request Tracking**: In-memory request tracking with automatic cleanup
- **CORS Configuration**: Controlled cross-origin access
- **Trusted Host Middleware**: Domain-based access control

### Database Security
- **Read-Only Transactions**: All database queries execute in read-only mode
- **Connection Timeouts**: Prevent hanging connections
- **Result Size Limiting**: Maximum 1000 rows per query
- **Connection Pooling**: Secure connection management with proper cleanup

### Error Handling & Privacy
- **Generic Error Messages**: Prevent information disclosure
- **IP Anonymization**: Log only partial IP addresses for privacy
- **No Query Logging**: User questions are not logged to prevent data leakage
- **Structured Error Responses**: Consistent error format across all endpoints

## 📈 **Monitoring & Observability**

### Health Monitoring
```json
{
  "status": "online",
  "service": "Natural Language to SQL API",
  "version": "1.0.0",
  "timestamp": "2025-11-20T10:30:00",
  "database_status": {
    "postgresql": "not_configured",
    "mysql": "not_configured", 
    "oracle": "not_configured"
  },
  "openai_configured": false
}
```

### Logging Structure
```
2025-11-20 10:30:00 - main - INFO - Received query request from 127.0.0.1... - question length: 45
2025-11-20 10:30:00 - main - INFO - Query completed successfully in 5.2ms. Returned 10 rows.
```

### Performance Metrics
- **Response Time Tracking**: Execution time logged for all requests
- **Query Success Rate**: Success/failure ratio monitoring
- **Rate Limit Events**: Track and alert on rate limiting
- **Database Connectivity**: Monitor connection pool health

## 🛠 **Development**

### Project Structure
```
nl-to-sql-solution/
├── main.py                 # FastAPI application core
├── mock_banking_data.py    # Realistic banking dataset
├── requirements.txt        # Python dependencies  
├── test_queries.md        # Comprehensive test scenarios
├── .env                   # Environment configuration (optional)
├── .github/
│   └── copilot-instructions.md  # AI coding guidelines
└── README.md              # This documentation
```

### Code Guidelines
- **PEP 8 Compliance**: Follow Python style guidelines
- **Type Hints**: Use type annotations for all functions
- **Docstrings**: Document all public functions and classes
- **Error Handling**: Comprehensive exception handling
- **Security First**: Validate all inputs and sanitize outputs

## 🚀 **Production Deployment**

### Docker Deployment (Recommended)
```dockerfile
FROM python:3.12-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
```

### Cloud Deployment Options
- **Azure App Service**: Direct Python deployment
- **AWS ECS/Fargate**: Containerized deployment  
- **Google Cloud Run**: Serverless container deployment
- **Heroku**: Git-based deployment with Procfile

### Production Checklist
- [ ] Set environment variables for database connections
- [ ] Configure OpenAI API key for advanced features
- [ ] Enable HTTPS with proper SSL certificates
- [ ] Set up monitoring and logging aggregation
- [ ] Configure database connection pooling for your workload
- [ ] Set up backup and disaster recovery procedures
- [ ] Implement CI/CD pipeline for automated deployments

## 🐛 **Troubleshooting**

### Common Issues

**Issue**: `pip: command not found`
```bash
# Solution: Use Python module syntax
python -m pip install -r requirements.txt
# Or use Windows launcher
py -m pip install -r requirements.txt
# Or use full path on Windows
& "$env:LOCALAPPDATA\Programs\Python\Python312\python.exe" -m pip install -r requirements.txt
```

**Issue**: `422 Unprocessable Entity` on API requests
```bash
# Solution: Check request format
{
  "question": "Your question here",
  "db_type": "postgresql"  # Must be one of: postgresql, mysql, oracle
}
```

**Issue**: Rate limiting errors (429)
```bash
# Solution: Wait 60 seconds between request bursts
# Rate limit: 10 requests per minute per IP
```

**Issue**: Database connection failures
```bash
# Solution: Verify connection strings in .env file
# Application will fall back to mock data if no database configured
```

### Performance Optimization
- **Connection Pooling**: Tune pool size based on concurrent users
- **Query Caching**: Consider Redis for frequent query results
- **Load Balancing**: Use multiple workers for high-traffic deployments
- **Database Indexing**: Optimize database indexes for common query patterns

## 📚 **Additional Resources**

### Documentation Links
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [OpenAI API Reference](https://platform.openai.com/docs/api-reference)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [Pydantic Documentation](https://pydantic-docs.helpmanual.io/)

### Example Use Cases
- **Business Intelligence**: Convert business questions to SQL for reporting
- **Database Exploration**: Help non-technical users explore database content
- **Educational Tool**: Teaching SQL concepts through natural language
- **API Integration**: Embed natural language querying in existing applications

### Extension Ideas
- **Query History**: Save and retrieve previous queries
- **Result Export**: Export results to CSV, Excel, or PDF
- **Chart Generation**: Visualize query results with charts
- **User Authentication**: Add user accounts and query permissions
- **Query Optimization**: Suggest performance improvements for generated SQL

## 🤝 **Support & Contact**

- **GitHub Repository**: https://github.com/sirrohan1708/nl-to-sql-solution
- **Issues & Features**: [GitHub Issues](https://github.com/sirrohan1708/nl-to-sql-solution/issues)
- **Documentation**: This README and inline code documentation
- **Testing Guide**: See `test_queries.md` for comprehensive test scenarios

## 📄 **License**

This project is licensed under the MIT License - feel free to use for learning and development.

---

**Built with ❤️ using FastAPI, OpenAI, and modern Python practices**
