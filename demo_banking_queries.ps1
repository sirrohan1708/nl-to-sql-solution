# Banking NL to SQL - Client Demo Script
# =======================================
# Ready-to-use demo queries for client presentations

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Banking NL to SQL - Client Demo" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Base URL
$baseUrl = "http://localhost:8000"

Write-Host "Testing API Health..." -ForegroundColor Yellow
curl.exe -X GET "$baseUrl/" | ConvertFrom-Json | ConvertTo-Json
Write-Host ""

Write-Host "Press any key for Demo Query 1..." -ForegroundColor Green
$null = $Host.UI.RawUI.ReadKey('NoEcho,IncludeKeyDown')
Write-Host ""

# Demo 1: Top Customers by Transaction Volume
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Demo 1: Top 10 Customers by Spending" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Question: 'Show me the top 10 customers by total transaction amount'" -ForegroundColor White
Write-Host ""
curl.exe -X POST "$baseUrl/query" `
  -H "Content-Type: application/json" `
  -d '{\"question\": \"Show me the top 10 customers by total transaction amount\"}' | ConvertFrom-Json | ConvertTo-Json -Depth 10
Write-Host ""

Write-Host "Press any key for Demo Query 2..." -ForegroundColor Green
$null = $Host.UI.RawUI.ReadKey('NoEcho,IncludeKeyDown')
Write-Host ""

# Demo 2: High-Value Transactions
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Demo 2: Large Transactions" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Question: 'Show me all high-value transactions above $1000'" -ForegroundColor White
Write-Host ""
curl.exe -X POST "$baseUrl/query" `
  -H "Content-Type: application/json" `
  -d '{\"question\": \"Show me all large transactions above 1000 dollars\"}' | ConvertFrom-Json | ConvertTo-Json -Depth 10
Write-Host ""

Write-Host "Press any key for Demo Query 3..." -ForegroundColor Green
$null = $Host.UI.RawUI.ReadKey('NoEcho,IncludeKeyDown')
Write-Host ""

# Demo 3: Loan Risk Analysis
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Demo 3: Loan Risk Analysis" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Question: 'Show me customers with defaulted or high-risk loans'" -ForegroundColor White
Write-Host ""
curl.exe -X POST "$baseUrl/query" `
  -H "Content-Type: application/json" `
  -d '{\"question\": \"Show me customers with defaulted loans\"}' | ConvertFrom-Json | ConvertTo-Json -Depth 10
Write-Host ""

Write-Host "Press any key for Demo Query 4..." -ForegroundColor Green
$null = $Host.UI.RawUI.ReadKey('NoEcho,IncludeKeyDown')
Write-Host ""

# Demo 4: Premium Customer Analysis
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Demo 4: Premium Customers by Balance" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Question: 'Show me top premium customers by account balance'" -ForegroundColor White
Write-Host ""
curl.exe -X POST "$baseUrl/query" `
  -H "Content-Type: application/json" `
  -d '{\"question\": \"Show me top premium customers by account balance\"}' | ConvertFrom-Json | ConvertTo-Json -Depth 10
Write-Host ""

Write-Host "Press any key for Demo Query 5..." -ForegroundColor Green
$null = $Host.UI.RawUI.ReadKey('NoEcho,IncludeKeyDown')
Write-Host ""

# Demo 5: Pending Transactions
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Demo 5: Pending/Failed Transactions" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Question: 'Show me all pending or failed transactions'" -ForegroundColor White
Write-Host ""
curl.exe -X POST "$baseUrl/query" `
  -H "Content-Type: application/json" `
  -d '{\"question\": \"Show me all pending transactions\"}' | ConvertFrom-Json | ConvertTo-Json -Depth 10
Write-Host ""

Write-Host "Press any key for Demo Query 6..." -ForegroundColor Green
$null = $Host.UI.RawUI.ReadKey('NoEcho,IncludeKeyDown')
Write-Host ""

# Demo 6: Customer Credit Scores
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Demo 6: Customers by Credit Score" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Question: 'Show me customers with highest credit scores'" -ForegroundColor White
Write-Host ""
curl.exe -X POST "$baseUrl/query" `
  -H "Content-Type: application/json" `
  -d '{\"question\": \"Show me customers with highest credit scores\"}' | ConvertFrom-Json | ConvertTo-Json -Depth 10
Write-Host ""

Write-Host "Press any key for Demo Query 7..." -ForegroundColor Green
$null = $Host.UI.RawUI.ReadKey('NoEcho,IncludeKeyDown')
Write-Host ""

# Demo 7: Loan Summary
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Demo 7: Largest Active Loans" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Question: 'Show me the largest active loans'" -ForegroundColor White
Write-Host ""
curl.exe -X POST "$baseUrl/query" `
  -H "Content-Type: application/json" `
  -d '{\"question\": \"Show me the largest active loans\"}' | ConvertFrom-Json | ConvertTo-Json -Depth 10
Write-Host ""

Write-Host "Press any key for Demo Query 8..." -ForegroundColor Green
$null = $Host.UI.RawUI.ReadKey('NoEcho,IncludeKeyDown')
Write-Host ""

# Demo 8: Recent Customers
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Demo 8: Recently Onboarded Customers" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Question: 'Show me the most recently registered customers'" -ForegroundColor White
Write-Host ""
curl.exe -X POST "$baseUrl/query" `
  -H "Content-Type: application/json" `
  -d '{\"question\": \"Show me the most recently registered customers\"}' | ConvertFrom-Json | ConvertTo-Json -Depth 10
Write-Host ""

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Demo Complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "View API Documentation: http://localhost:8000/docs" -ForegroundColor Yellow
Write-Host "View Database Schema: http://localhost:8000/schema" -ForegroundColor Yellow
