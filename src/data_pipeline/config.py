"""
Configuration file for the financial data pipeline
"""
import os

# Base paths
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
DATA_PIPELINE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(PROJECT_ROOT, 'data')

# Medallion architecture paths (separate from code)
BRONZE_DIR = os.path.join(DATA_DIR, 'bronze')
SILVER_DIR = os.path.join(DATA_DIR, 'silver')
GOLD_DIR = os.path.join(DATA_DIR, 'gold')

# Company folders
EMPRESAS_DIR = os.path.join(DATA_DIR, 'output', 'EMPRESAS')

# PostgreSQL Database Configuration
DB_CONFIG = {
    'host': 'localhost',
    'port': 5432,
    'database': 'financial_data',
    'user': 'postgres',
    'password': 'postgres'  # Muda para a tua password
}

# Top 10 tech companies
TECH_COMPANIES = {
    'AAPL': 'Apple Inc.',
    'MSFT': 'Microsoft Corporation',
    'GOOGL': 'Alphabet Inc.',
    'AMZN': 'Amazon.com Inc.',
    'NVDA': 'NVIDIA Corporation',
    'META': 'Meta Platforms Inc.',
    'TSLA': 'Tesla Inc.',
    'AVGO': 'Broadcom Inc.',
    'ASML': 'ASML Holding N.V.',
    'NFLX': 'Netflix Inc.'
}

# Financial statement types
STATEMENT_TYPES = ['income', 'balance-sheet', 'cash-flow']

# Years of data to fetch
YEARS_OF_DATA = 5
