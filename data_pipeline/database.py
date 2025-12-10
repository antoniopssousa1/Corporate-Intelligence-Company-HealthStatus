"""
Database schema and initialization for the financial data pipeline
Using PostgreSQL with Medallion Architecture (Bronze -> Silver -> Gold)
"""
import psycopg2
from psycopg2 import sql
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config import DB_CONFIG

def create_database_if_not_exists():
    """Create the database if it doesn't exist"""
    conn = psycopg2.connect(
        host=DB_CONFIG['host'],
        port=DB_CONFIG['port'],
        user=DB_CONFIG['user'],
        password=DB_CONFIG['password'],
        database='postgres'
    )
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cursor = conn.cursor()
    
    # Check if database exists
    cursor.execute("SELECT 1 FROM pg_database WHERE datname = %s", (DB_CONFIG['database'],))
    if not cursor.fetchone():
        cursor.execute(sql.SQL("CREATE DATABASE {}").format(sql.Identifier(DB_CONFIG['database'])))
        print(f"Database '{DB_CONFIG['database']}' created successfully!")
    
    cursor.close()
    conn.close()

def init_database():
    """Initialize the PostgreSQL database with all required tables"""
    # First ensure database exists
    create_database_if_not_exists()
    
    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    # =====================================================
    # BRONZE LAYER - Raw data as extracted from source
    # =====================================================
    
    # Raw Income Statement
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS bronze_income_statement (
            id SERIAL PRIMARY KEY,
            ticker VARCHAR(10) NOT NULL,
            company_name VARCHAR(255),
            fiscal_year VARCHAR(20),
            metric_name VARCHAR(255),
            metric_value DOUBLE PRECISION,
            raw_value VARCHAR(100),
            extracted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Raw Balance Sheet
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS bronze_balance_sheet (
            id SERIAL PRIMARY KEY,
            ticker VARCHAR(10) NOT NULL,
            company_name VARCHAR(255),
            fiscal_year VARCHAR(20),
            metric_name VARCHAR(255),
            metric_value DOUBLE PRECISION,
            raw_value VARCHAR(100),
            extracted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Raw Cash Flow Statement
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS bronze_cash_flow (
            id SERIAL PRIMARY KEY,
            ticker VARCHAR(10) NOT NULL,
            company_name VARCHAR(255),
            fiscal_year VARCHAR(20),
            metric_name VARCHAR(255),
            metric_value DOUBLE PRECISION,
            raw_value VARCHAR(100),
            extracted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # =====================================================
    # SILVER LAYER - Cleaned and standardized data
    # =====================================================
    
    # Companies dimension
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS silver_companies (
            ticker VARCHAR(10) PRIMARY KEY,
            company_name VARCHAR(255) NOT NULL,
            sector VARCHAR(100) DEFAULT 'Technology',
            last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Standardized Income Statement
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS silver_income_statement (
            id SERIAL PRIMARY KEY,
            ticker VARCHAR(10) NOT NULL REFERENCES silver_companies(ticker),
            fiscal_year INTEGER,
            revenue DOUBLE PRECISION,
            cost_of_revenue DOUBLE PRECISION,
            gross_profit DOUBLE PRECISION,
            operating_expenses DOUBLE PRECISION,
            operating_income DOUBLE PRECISION,
            net_income DOUBLE PRECISION,
            ebitda DOUBLE PRECISION,
            eps_basic DOUBLE PRECISION,
            eps_diluted DOUBLE PRECISION
        )
    ''')
    
    # Standardized Balance Sheet
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS silver_balance_sheet (
            id SERIAL PRIMARY KEY,
            ticker VARCHAR(10) NOT NULL REFERENCES silver_companies(ticker),
            fiscal_year INTEGER,
            total_assets DOUBLE PRECISION,
            total_liabilities DOUBLE PRECISION,
            total_equity DOUBLE PRECISION,
            current_assets DOUBLE PRECISION,
            current_liabilities DOUBLE PRECISION,
            cash_and_equivalents DOUBLE PRECISION,
            total_debt DOUBLE PRECISION,
            retained_earnings DOUBLE PRECISION
        )
    ''')
    
    # Standardized Cash Flow
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS silver_cash_flow (
            id SERIAL PRIMARY KEY,
            ticker VARCHAR(10) NOT NULL REFERENCES silver_companies(ticker),
            fiscal_year INTEGER,
            operating_cash_flow DOUBLE PRECISION,
            investing_cash_flow DOUBLE PRECISION,
            financing_cash_flow DOUBLE PRECISION,
            free_cash_flow DOUBLE PRECISION,
            capital_expenditures DOUBLE PRECISION,
            dividends_paid DOUBLE PRECISION,
            net_change_in_cash DOUBLE PRECISION
        )
    ''')
    
    # =====================================================
    # GOLD LAYER - Business-ready analytics and KPIs
    # =====================================================
    
    # Financial Health Score
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS gold_financial_health (
            id SERIAL PRIMARY KEY,
            ticker VARCHAR(10) NOT NULL REFERENCES silver_companies(ticker),
            company_name VARCHAR(255),
            fiscal_year INTEGER,
            -- Liquidity Ratios
            current_ratio DOUBLE PRECISION,
            quick_ratio DOUBLE PRECISION,
            cash_ratio DOUBLE PRECISION,
            -- Profitability Ratios
            gross_margin DOUBLE PRECISION,
            operating_margin DOUBLE PRECISION,
            net_margin DOUBLE PRECISION,
            roe DOUBLE PRECISION,
            roa DOUBLE PRECISION,
            -- Leverage Ratios
            debt_to_equity DOUBLE PRECISION,
            debt_to_assets DOUBLE PRECISION,
            interest_coverage DOUBLE PRECISION,
            -- Efficiency Ratios
            asset_turnover DOUBLE PRECISION,
            -- Cash Flow Ratios
            operating_cash_flow_ratio DOUBLE PRECISION,
            free_cash_flow_margin DOUBLE PRECISION,
            -- Health Score (0-100)
            health_score DOUBLE PRECISION,
            health_status VARCHAR(50),
            analysis_notes TEXT,
            calculated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # KPI Summary for Dashboard
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS gold_kpi_dashboard (
            id SERIAL PRIMARY KEY,
            ticker VARCHAR(10) NOT NULL REFERENCES silver_companies(ticker),
            company_name VARCHAR(255),
            fiscal_year INTEGER,
            -- Key Metrics
            revenue DOUBLE PRECISION,
            revenue_growth DOUBLE PRECISION,
            net_income DOUBLE PRECISION,
            profit_growth DOUBLE PRECISION,
            total_assets DOUBLE PRECISION,
            total_debt DOUBLE PRECISION,
            free_cash_flow DOUBLE PRECISION,
            -- Ratios
            current_ratio DOUBLE PRECISION,
            debt_to_equity DOUBLE PRECISION,
            net_margin DOUBLE PRECISION,
            roe DOUBLE PRECISION,
            -- Scores
            health_score DOUBLE PRECISION,
            health_status VARCHAR(50),
            -- Rankings
            revenue_rank INTEGER,
            profit_rank INTEGER,
            health_rank INTEGER
        )
    ''')
    
    # Trend Analysis
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS gold_trends (
            id SERIAL PRIMARY KEY,
            ticker VARCHAR(10) NOT NULL REFERENCES silver_companies(ticker),
            company_name VARCHAR(255),
            metric_name VARCHAR(100),
            year_1 DOUBLE PRECISION,
            year_2 DOUBLE PRECISION,
            year_3 DOUBLE PRECISION,
            year_4 DOUBLE PRECISION,
            year_5 DOUBLE PRECISION,
            cagr_5y DOUBLE PRECISION,
            trend_direction VARCHAR(20)
        )
    ''')
    
    # Create indexes for better performance
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_bronze_income_ticker ON bronze_income_statement(ticker)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_bronze_balance_ticker ON bronze_balance_sheet(ticker)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_bronze_cash_ticker ON bronze_cash_flow(ticker)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_silver_income_ticker ON silver_income_statement(ticker)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_silver_balance_ticker ON silver_balance_sheet(ticker)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_silver_cash_ticker ON silver_cash_flow(ticker)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_gold_health_ticker ON gold_financial_health(ticker)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_gold_kpi_ticker ON gold_kpi_dashboard(ticker)')
    
    conn.commit()
    cursor.close()
    conn.close()
    print(f"PostgreSQL database '{DB_CONFIG['database']}' initialized successfully!")

def get_connection():
    """Get a database connection"""
    return psycopg2.connect(**DB_CONFIG)

if __name__ == '__main__':
    init_database()
