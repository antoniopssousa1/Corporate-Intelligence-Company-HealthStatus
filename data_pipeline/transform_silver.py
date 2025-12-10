"""
SILVER LAYER - Transform and clean bronze data into standardized format
This script processes raw data into structured, normalized tables
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database import get_connection, init_database
from config import TECH_COMPANIES

# Metric name mappings for standardization
INCOME_METRICS = {
    'Revenue': 'revenue',
    'Total Revenue': 'revenue',
    'Net Sales': 'revenue',
    'Cost of Revenue': 'cost_of_revenue',
    'Cost of Goods Sold': 'cost_of_revenue',
    'Gross Profit': 'gross_profit',
    'Operating Expenses': 'operating_expenses',
    'Total Operating Expenses': 'operating_expenses',
    'Operating Income': 'operating_income',
    'Net Income': 'net_income',
    'Net Income Common': 'net_income',
    'EBITDA': 'ebitda',
    'EPS (Basic)': 'eps_basic',
    'EPS Basic': 'eps_basic',
    'EPS (Diluted)': 'eps_diluted',
    'EPS Diluted': 'eps_diluted',
}

BALANCE_METRICS = {
    'Total Assets': 'total_assets',
    'Total Liabilities': 'total_liabilities',
    'Total Equity': 'total_equity',
    "Shareholders' Equity": 'total_equity',
    'Stockholders Equity': 'total_equity',
    'Current Assets': 'current_assets',
    'Total Current Assets': 'current_assets',
    'Current Liabilities': 'current_liabilities',
    'Total Current Liabilities': 'current_liabilities',
    'Cash & Cash Equivalents': 'cash_and_equivalents',
    'Cash and Cash Equivalents': 'cash_and_equivalents',
    'Cash & Equivalents': 'cash_and_equivalents',
    'Total Debt': 'total_debt',
    'Long-Term Debt': 'total_debt',
    'Retained Earnings': 'retained_earnings',
}

CASHFLOW_METRICS = {
    'Operating Cash Flow': 'operating_cash_flow',
    'Cash from Operations': 'operating_cash_flow',
    'Net Cash from Operating Activities': 'operating_cash_flow',
    'Investing Cash Flow': 'investing_cash_flow',
    'Cash from Investing': 'investing_cash_flow',
    'Net Cash from Investing Activities': 'investing_cash_flow',
    'Financing Cash Flow': 'financing_cash_flow',
    'Cash from Financing': 'financing_cash_flow',
    'Net Cash from Financing Activities': 'financing_cash_flow',
    'Free Cash Flow': 'free_cash_flow',
    'Capital Expenditures': 'capital_expenditures',
    'Capital Expenditure': 'capital_expenditures',
    'Dividends Paid': 'dividends_paid',
    'Net Change in Cash': 'net_change_in_cash',
    'Change in Cash': 'net_change_in_cash',
}


def transform_to_silver():
    """Transform bronze data to silver layer"""
    print("=" * 60)
    print("SILVER LAYER - Data Transformation")
    print("=" * 60)
    
    conn = get_connection()
    cursor = conn.cursor()
    
    # Clear existing silver data (except companies as it's a dimension)
    cursor.execute("TRUNCATE TABLE silver_income_statement CASCADE")
    cursor.execute("TRUNCATE TABLE silver_balance_sheet CASCADE")
    cursor.execute("TRUNCATE TABLE silver_cash_flow CASCADE")
    cursor.execute("TRUNCATE TABLE silver_companies CASCADE")
    conn.commit()
    
    # Insert companies
    print("\nCreating company dimension...")
    for ticker, company_name in TECH_COMPANIES.items():
        cursor.execute('''
            INSERT INTO silver_companies (ticker, company_name, sector)
            VALUES (%s, %s, %s)
            ON CONFLICT (ticker) DO UPDATE SET company_name = EXCLUDED.company_name
        ''', (ticker, company_name, 'Technology'))
    conn.commit()
    
    # Process each company
    for ticker, company_name in TECH_COMPANIES.items():
        print(f"\n[{ticker}] Processing {company_name}...")
        
        # Get distinct years from bronze data
        cursor.execute('''
            SELECT DISTINCT fiscal_year FROM bronze_income_statement 
            WHERE ticker = %s AND fiscal_year ~ '^[0-9]{4}$'
            ORDER BY fiscal_year DESC
            LIMIT 5
        ''', (ticker,))
        years = [row[0] for row in cursor.fetchall()]
        
        for year in years:
            # Process Income Statement
            income_data = {'ticker': ticker, 'fiscal_year': int(year)}
            cursor.execute('''
                SELECT metric_name, metric_value FROM bronze_income_statement
                WHERE ticker = %s AND fiscal_year = %s
            ''', (ticker, year))
            
            for metric_name, value in cursor.fetchall():
                if metric_name in INCOME_METRICS and value is not None:
                    income_data[INCOME_METRICS[metric_name]] = value
            
            if len(income_data) > 2:
                cols = ', '.join(income_data.keys())
                placeholders = ', '.join(['%s'] * len(income_data))
                cursor.execute(f'''
                    INSERT INTO silver_income_statement ({cols}) VALUES ({placeholders})
                ''', list(income_data.values()))
            
            # Process Balance Sheet
            balance_data = {'ticker': ticker, 'fiscal_year': int(year)}
            cursor.execute('''
                SELECT metric_name, metric_value FROM bronze_balance_sheet
                WHERE ticker = %s AND fiscal_year = %s
            ''', (ticker, year))
            
            for metric_name, value in cursor.fetchall():
                if metric_name in BALANCE_METRICS and value is not None:
                    balance_data[BALANCE_METRICS[metric_name]] = value
            
            if len(balance_data) > 2:
                cols = ', '.join(balance_data.keys())
                placeholders = ', '.join(['%s'] * len(balance_data))
                cursor.execute(f'''
                    INSERT INTO silver_balance_sheet ({cols}) VALUES ({placeholders})
                ''', list(balance_data.values()))
            
            # Process Cash Flow
            cashflow_data = {'ticker': ticker, 'fiscal_year': int(year)}
            cursor.execute('''
                SELECT metric_name, metric_value FROM bronze_cash_flow
                WHERE ticker = %s AND fiscal_year = %s
            ''', (ticker, year))
            
            for metric_name, value in cursor.fetchall():
                if metric_name in CASHFLOW_METRICS and value is not None:
                    cashflow_data[CASHFLOW_METRICS[metric_name]] = value
            
            if len(cashflow_data) > 2:
                cols = ', '.join(cashflow_data.keys())
                placeholders = ', '.join(['%s'] * len(cashflow_data))
                cursor.execute(f'''
                    INSERT INTO silver_cash_flow ({cols}) VALUES ({placeholders})
                ''', list(cashflow_data.values()))
        
        conn.commit()
        print(f"  ✓ Processed {len(years)} years of data")
    
    cursor.close()
    conn.close()
    
    print("\n" + "=" * 60)
    print("Silver transformation complete!")
    print("=" * 60)


if __name__ == '__main__':
    transform_to_silver()
