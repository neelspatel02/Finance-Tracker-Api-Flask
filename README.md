# Finance Tracker

This is the api verson of the Finance-Tracker i made with flask. [Here](https://github.com/neelspatel02/Finance-Tracker)


## Stack
- Python / Flask
- SQLite
- Flask-Login

## Setup
1. Clone the repo
2. Install dependencies: `pip install -r requirements.txt`
3. Create `.env` file (see `.env.example`)
4. Run: `python app.py`

## API Endpoints
### Auth
- POST /api/auth/register
- POST /api/auth/login
- POST /api/auth/logout

### Transactions
- GET    /api/transactions
- POST   /api/transactions
- DELETE /api/transactions/<id>

### Categories
- GET    /api/categories
- POST   /api/categories
- DELETE /api/categories/<id>

### Analysis
- GET /api/analysis
- GET /api/analysis/yearly
- GET /api/analysis/monthly
- GET /api/analysis/weekly
- GET /api/analysis/categories

*will be adding JWT and other features such as AI integration in future* 