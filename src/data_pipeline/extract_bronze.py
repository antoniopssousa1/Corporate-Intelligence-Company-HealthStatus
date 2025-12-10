"""
BRONZE LAYER - Extract raw financial data using yfinance
This script fetches income statement, balance sheet, and cash flow data
"""
import pandas as pd
import yfinance as yf
import time
import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import TECH_COMPANIES, BRONZE_DIR, EMPRESAS_DIR
from database import get_connection, init_database


def extract_to_bronze(ticker, company_name):
    """Extract all financial statements for a company into bronze layer using yfinance"""
    conn = get_connection()
    cursor = conn.cursor()
    
    print(f"  Downloading data from Yahoo Finance...")
    
    try:
        stock = yf.Ticker(ticker)
        
        # Get financial statements (annual)
        income_stmt = stock.income_stmt
        balance_sheet = stock.balance_sheet
        cash_flow = stock.cashflow
        
        all_dataframes = {}
        
        # Process Income Statement
        if income_stmt is not None and not income_stmt.empty:
            print(f"  ✓ Income Statement: {income_stmt.shape[1]} years")
            for col in income_stmt.columns:
                year = str(col.year) if hasattr(col, 'year') else str(col)[:4]
                for metric_name in income_stmt.index:
                    value = income_stmt.loc[metric_name, col]
                    if pd.notna(value):
                        cursor.execute('''
                            INSERT INTO bronze_income_statement 
                            (ticker, company_name, fiscal_year, metric_name, metric_value, raw_value)
                            VALUES (%s, %s, %s, %s, %s, %s)
                        ''', (ticker, company_name, year, str(metric_name), float(value), str(value)))
            
            # Transpose for Excel (metrics as rows, years as columns)
            df = income_stmt.T
            df.index = [str(idx.year) if hasattr(idx, 'year') else str(idx)[:4] for idx in df.index]
            all_dataframes['income'] = df.reset_index().rename(columns={'index': 'Year'})
        
        # Process Balance Sheet
        if balance_sheet is not None and not balance_sheet.empty:
            print(f"  ✓ Balance Sheet: {balance_sheet.shape[1]} years")
            for col in balance_sheet.columns:
                year = str(col.year) if hasattr(col, 'year') else str(col)[:4]
                for metric_name in balance_sheet.index:
                    value = balance_sheet.loc[metric_name, col]
                    if pd.notna(value):
                        cursor.execute('''
                            INSERT INTO bronze_balance_sheet 
                            (ticker, company_name, fiscal_year, metric_name, metric_value, raw_value)
                            VALUES (%s, %s, %s, %s, %s, %s)
                        ''', (ticker, company_name, year, str(metric_name), float(value), str(value)))
            
            df = balance_sheet.T
            df.index = [str(idx.year) if hasattr(idx, 'year') else str(idx)[:4] for idx in df.index]
            all_dataframes['balance-sheet'] = df.reset_index().rename(columns={'index': 'Year'})
        
        # Process Cash Flow
        if cash_flow is not None and not cash_flow.empty:
            print(f"  ✓ Cash Flow: {cash_flow.shape[1]} years")
            for col in cash_flow.columns:
                year = str(col.year) if hasattr(col, 'year') else str(col)[:4]
                for metric_name in cash_flow.index:
                    value = cash_flow.loc[metric_name, col]
                    if pd.notna(value):
                        cursor.execute('''
                            INSERT INTO bronze_cash_flow 
                            (ticker, company_name, fiscal_year, metric_name, metric_value, raw_value)
                            VALUES (%s, %s, %s, %s, %s, %s)
                        ''', (ticker, company_name, year, str(metric_name), float(value), str(value)))
            
            df = cash_flow.T
            df.index = [str(idx.year) if hasattr(idx, 'year') else str(idx)[:4] for idx in df.index]
            all_dataframes['cash-flow'] = df.reset_index().rename(columns={'index': 'Year'})
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return all_dataframes
        
    except Exception as e:
        print(f"  ⚠ Error: {e}")
        conn.rollback()
        cursor.close()
        conn.close()
        return {}


def save_to_excel(ticker, company_name, dataframes):
    """Save financial statements to Excel files in company folder"""
    company_folder = os.path.join(EMPRESAS_DIR, f"{ticker}_{company_name.replace(' ', '_').replace('.', '').replace(',', '')}")
    os.makedirs(company_folder, exist_ok=True)
    
    file_names = {
        'income': 'income_statement.xlsx',
        'balance-sheet': 'balance_sheet.xlsx',
        'cash-flow': 'cash_flow.xlsx'
    }
    
    for stmt_type, df in dataframes.items():
        if df is not None and not df.empty:
            file_path = os.path.join(company_folder, file_names[stmt_type])
            df.to_excel(file_path, index=False, sheet_name=stmt_type.replace('-', '_'))
            print(f"    Saved: {file_names[stmt_type]} ({len(df)} rows)")
    
    return company_folder


def run_bronze_extraction():
    """Main function to extract all data into bronze layer"""
    print("=" * 60)
    print("BRONZE LAYER - Raw Data Extraction (yfinance)")
    print("=" * 60)
    
    # Initialize database
    init_database()
    
    # Clear existing bronze data
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM bronze_income_statement")
    cursor.execute("DELETE FROM bronze_balance_sheet")
    cursor.execute("DELETE FROM bronze_cash_flow")
    conn.commit()
    cursor.close()
    conn.close()
    
    print(f"\nExtracting data for {len(TECH_COMPANIES)} companies...\n")
    
    for ticker, company_name in TECH_COMPANIES.items():
        print(f"\n[{ticker}] {company_name}")
        dataframes = extract_to_bronze(ticker, company_name)
        
        if dataframes:
            folder = save_to_excel(ticker, company_name, dataframes)
            print(f"  → Saved to: {folder}")
        else:
            print(f"  ⚠ No data extracted")
        
        time.sleep(0.5)  # Rate limiting between companies
    
    print("\n" + "=" * 60)
    print("Bronze extraction complete!")
    print("=" * 60)

if __name__ == '__main__':
    run_bronze_extraction()
