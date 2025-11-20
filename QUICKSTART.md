# 🚀 Quick Start Guide - Banking NL to SQL

## ⚡ 30-Second Test

The server is already running! Test it immediately:

```powershell
curl.exe -X POST "http://localhost:8000/query" -H "Content-Type: application/json" -d '{\"question\": \"Show me top 5 customers by spending\"}'
```

Or open in browser: **http://localhost:8000/docs**

---

## 📊 What's Available

### Live Data (Ready for Demo):
- ✅ **100 Banking Customers** with realistic profiles
- ✅ **~1,000 Transactions** across multiple categories
- ✅ **~120 Loans** (mortgages, auto, personal, business)
- ✅ **Credit scores** (600-850)
- ✅ **Account balances** ($500-$250K)
- ✅ **25 US cities**

### API Endpoints:
- `POST /query` - Main NL to SQL endpoint
- `GET /schema` - View database schema
- `GET /` - Health check
- `GET /docs` - Interactive API documentation

---

## 🎯 Try These Questions

Copy and paste these into the API or use curl:

### Customer Insights:
```
"Show me top 10 customers by total spending"
"Show me premium customers by account balance"
"Show me customers with highest credit scores"
```

### Transaction Analysis:
```
"Show me large transactions above $1000"
"Show me pending transactions"
"Show me recent completed transactions"
```

### Loan Management:
```
"Show me customers with defaulted loans"
"Show me the largest active loans"
"Show me customers with highest total debt"
```

---

## 🎬 Run Full Demo

For client presentations:
```powershell
.\demo_banking_queries.ps1
```

This runs 8 pre-configured queries with formatted output.

---

## 🔧 Configuration

### Current Mode: **MOCK MODE** ✅
- Works without database
- Works without OpenAI API
- Uses realistic banking data
- Perfect for demos and testing

### To Enable Real Features:

#### 1. OpenAI Integration (Optional)
Edit `.env` file:
```
OPENAI_API_KEY=sk-your-api-key-here
```

#### 2. PostgreSQL Database (Optional)
Edit `.env` file:
```
DATABASE_URL=postgresql://readonly_user:password@localhost:5432/banking_db
```

**Note:** Mock mode is recommended for client demos!

---

## 📖 Documentation

- `README.md` - Complete technical documentation
- `PRESENTATION_GUIDE.md` - Client presentation walkthrough
- `DEMO_QUERIES.md` - 20+ example questions
- `http://localhost:8000/docs` - Interactive API docs

---

## 🔒 Security Features

### Automatic Protection:
- ✅ Only SELECT queries allowed
- ✅ Blocks: DELETE, UPDATE, INSERT, DROP, ALTER, etc.
- ✅ Auto-adds LIMIT (max 1000 rows)
- ✅ Query timeout (30 seconds)
- ✅ Full audit logging
- ✅ SQL injection prevention

### Test Security:
```powershell
curl.exe -X POST "http://localhost:8000/query" -H "Content-Type: application/json" -d '{\"question\": \"DELETE FROM customers\"}'
```
**Expected:** ❌ BLOCKED with error message

---

## 🐛 Troubleshooting

### Server Not Running?
```powershell
uvicorn main:app --reload
```

### Check Server Status:
```powershell
curl.exe http://localhost:8000/
```

### View Logs:
Check the terminal where you started the server for detailed logs.

### Port Already in Use?
```powershell
uvicorn main:app --reload --port 8001
```

---

## 💡 Pro Tips

1. **Use Interactive Docs:** `http://localhost:8000/docs` has a "Try it out" button
2. **Check Generated SQL:** Every response includes the SQL that was generated
3. **View Execution Time:** Responses show query performance in milliseconds
4. **Explore Schema:** `http://localhost:8000/schema` shows all tables and columns
5. **Refine Questions:** If results aren't what you expect, try rephrasing

---

## 📊 Sample Response

```json
{
  "sql": "SELECT c.first_name, c.last_name, SUM(t.amount) as total_spent FROM customers c JOIN transactions t ON c.customer_id = t.customer_id WHERE t.status = 'completed' GROUP BY c.customer_id, c.first_name, c.last_name ORDER BY total_spent DESC LIMIT 10",
  "explanation": "Returns top 10 customers by total transaction spending with completed transactions only.",
  "result": [
    {
      "first_name": "Richard",
      "last_name": "Walker",
      "total_spent": 48050.4
    }
  ],
  "execution_time_ms": 15.65
}
```

---

## 🎯 Next Steps

1. ✅ Test with sample queries (see above)
2. ✅ Open interactive docs: `http://localhost:8000/docs`
3. ✅ Review presentation guide: `PRESENTATION_GUIDE.md`
4. ✅ Run full demo script: `.\demo_banking_queries.ps1`
5. ✅ Customize for your needs

---

## 📞 Key Files

- `main.py` - Core application (600+ lines)
- `mock_banking_data.py` - 100 customers, 1000+ transactions, 120+ loans
- `requirements.txt` - Python dependencies
- `.env` - Configuration (empty for mock mode)

---

**You're ready to demo! 🎉**

For a complete walkthrough, see `PRESENTATION_GUIDE.md`
