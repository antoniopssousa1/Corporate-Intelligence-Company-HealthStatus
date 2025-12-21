"""
Database schema and initialization for the financial data pipeline
Using PostgreSQL with Medallion Architecture (Bronze -> Silver -> Gold)
"""
import psycopg2
from psycopg2 import sql
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import os
import sys

# O que isto faz basicamente é permitir importar o config.py que está noutro ficheiro
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config import DB_CONFIG #importamos as tais configsda db

def create_database_if_not_exists(): #Funcao para criar a db se nao existir
    conn = psycopg2.connect(
        host=DB_CONFIG['host'],
        port=DB_CONFIG['port'],
        user=DB_CONFIG['user'],
        password=DB_CONFIG['password'],
        database='postgres'
    )
    #todos estes parametros estao pre-definidos no config.py

    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    #o que faz esta linha é definir o isolation level para autocommit, ou seja, cada comando SQL é automaticamente confirmado sem necessidade de chamar explicitamente o commit. Isto é importante quando se está a criar uma base de dados, porque algumas operações (como CREATE DATABASE) não podem ser executadas dentro de uma transação.
    cursor = conn.cursor() #criar um cursor para executar comandos SQL
    
    # ver se a db existe, claro que existe foi acabada de criar mas é so para garantir
    cursor.execute("SELECT 1 FROM pg_database WHERE datname = %s", (DB_CONFIG['database'],)) #o que isto faz é verificar se a base de dados com o nome especificado em DB_CONFIG['database'] já existe no servidor PostgreSQL. Ele faz isso consultando a tabela do sistema pg_database, que contém informações sobre todas as bases de dados no servidor.
    if not cursor.fetchone(): #se nao existir cria a db basicamente
        cursor.execute(sql.SQL("CREATE DATABASE {}").format(sql.Identifier(DB_CONFIG['database'])))
        print(f"Database '{DB_CONFIG['database']}' created successfully!")
    
    cursor.close()
    conn.close()

def init_database(): #vamos iniciar a db com as tabelas necessarias
    
    create_database_if_not_exists() #chamar a funcao para criar 
    
    conn = psycopg2.connect(**DB_CONFIG) #ligar à db ja criada os ** é para desempacotar o dicionario
    cursor = conn.cursor() #ligar o cursor para executar comandos SQL
    

    #bronze layer - raw data
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
    
    #ok em principio ja temos a bronze layer criada com as tabelas necessarias
    
    #agora criamos as silver layer - cleaned and standardized data
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
