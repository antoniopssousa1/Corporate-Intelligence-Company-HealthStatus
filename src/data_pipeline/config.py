"""
Configuration file for the financial data pipeline
"""
import os

# Path configs
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')) #o que isto faz basicamente é vai ao path onde está o config.py, sobe 2 niveis, 1 para src, 1 para Trabalho, e assim o project root fica definido como o path Trabalho
DATA_PIPELINE_DIR = os.path.dirname(os.path.abspath(__file__)) # src/data_pipeline
DATA_DIR = os.path.join(PROJECT_ROOT, 'data')# o data dir fica definido como o path Trabalho/data

# Arquitetura Medallion
BRONZE_DIR = os.path.join(DATA_DIR, 'bronze') #o bronze dir fica definido como o path Trabalho/data/bronze
SILVER_DIR = os.path.join(DATA_DIR, 'silver')#o silver dir fica definido como o path Trabalho/data/silver
GOLD_DIR = os.path.join(DATA_DIR, 'gold')#o gold dir fica definido como o path Trabalho/data/gold

# Folders de Empresas
EMPRESAS_DIR = os.path.join(DATA_DIR, 'output', 'EMPRESAS')#o EMPRESAS dir fica definido como o path Trabalho/data/output/EMPRESAS

# Configuração para ligar à base de dados PostgreSQL
DB_CONFIG = {
    'host': 'localhost',
    'port': 5432,
    'database': 'financial_data',
    'user': 'postgres',
    'password': 'postgres'  
}

# Agarrar no ticker das 10 maiores tech companies por market cap
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


STATEMENT_TYPES = ['income', 'balance-sheet', 'cash-flow'] #especificar os statements que quero

# quantos anos de dados financeiros quero puxar, limite sao 5 yfinance nao deixa mais... 
YEARS_OF_DATA = 5
