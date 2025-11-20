<!-- Use this file to provide workspace-specific custom instructions to Copilot. For more details, visit https://code.visualstudio.com/docs/copilot/copilot-customization#_use-a-githubcopilotinstructionsmd-file -->

# Natural Language to SQL Project

## Project Overview
This is a FastAPI-based application that converts natural language questions into SQL queries using OpenAI's API, validates them for safety, and executes them on a PostgreSQL database.

## Code Style and Standards
- Follow PEP 8 Python style guidelines
- Use type hints for all function parameters and return values
- Include docstrings for all functions and classes
- Keep functions focused and modular
- Use meaningful variable names

## Security Considerations
- Only SELECT queries should be allowed
- Always validate SQL before execution
- Use parameterized queries when possible
- Enforce row limits on all queries
- Use read-only database credentials

## Architecture
- **NL Parser**: Converts natural language to SQL using OpenAI
- **Validator**: Ensures only safe SELECT queries are executed
- **Executor**: Runs validated queries with timeout and limits
- **API**: FastAPI endpoints for handling requests

## Testing
- Test SQL validation with various dangerous commands
- Test query generation with edge cases
- Mock database responses for offline testing
- Verify error handling for all failure modes
