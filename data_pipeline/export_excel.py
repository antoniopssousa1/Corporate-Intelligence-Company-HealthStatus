"""
EXPORT TO EXCEL - Export gold layer data for Self-Service BI
Creates Excel files ready for Power BI / Excel dashboards
"""
import pandas as pd
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database import get_connection
from config import GOLD_DIR, EMPRESAS_DIR, TECH_COMPANIES


def export_to_excel():
    """Export all gold layer tables to Excel for BI consumption"""
    print("=" * 60)
    print("EXPORT TO EXCEL - Self-Service BI Ready")
    print("=" * 60)
    
    conn = get_connection()
    
    # Create output directory
    output_dir = os.path.join(GOLD_DIR, 'excel_export')
    os.makedirs(output_dir, exist_ok=True)
    
    # 1. Export KPI Dashboard (main fact table)
    print("\n📊 Exporting KPI Dashboard...")
    df_kpi = pd.read_sql('''
        SELECT 
            ticker as "Ticker",
            company_name as "Company",
            fiscal_year as "Year",
            revenue as "Revenue",
            revenue_growth as "Revenue Growth %",
            net_income as "Net Income",
            profit_growth as "Profit Growth %",
            total_assets as "Total Assets",
            total_debt as "Total Debt",
            free_cash_flow as "Free Cash Flow",
            current_ratio as "Current Ratio",
            debt_to_equity as "Debt to Equity",
            net_margin as "Net Margin %",
            roe as "ROE %",
            health_score as "Health Score",
            health_status as "Health Status",
            revenue_rank as "Revenue Rank",
            profit_rank as "Profit Rank",
            health_rank as "Health Rank"
        FROM gold_kpi_dashboard
        ORDER BY fiscal_year DESC, ticker
    ''', conn)
    
    kpi_path = os.path.join(output_dir, 'kpi_dashboard.xlsx')
    df_kpi.to_excel(kpi_path, index=False, sheet_name='KPIs')
    print(f"  ✓ Saved: {kpi_path}")
    
    # 2. Export Financial Health Analysis
    print("\n📊 Exporting Financial Health Analysis...")
    df_health = pd.read_sql('''
        SELECT 
            ticker as "Ticker",
            company_name as "Company",
            fiscal_year as "Year",
            current_ratio as "Current Ratio",
            quick_ratio as "Quick Ratio",
            cash_ratio as "Cash Ratio",
            gross_margin as "Gross Margin",
            operating_margin as "Operating Margin",
            net_margin as "Net Margin",
            roe as "ROE",
            roa as "ROA",
            debt_to_equity as "Debt to Equity",
            debt_to_assets as "Debt to Assets",
            asset_turnover as "Asset Turnover",
            operating_cash_flow_ratio as "OCF Ratio",
            free_cash_flow_margin as "FCF Margin",
            health_score as "Health Score",
            health_status as "Health Status",
            analysis_notes as "Analysis Notes"
        FROM gold_financial_health
        ORDER BY fiscal_year DESC, ticker
    ''', conn)
    
    health_path = os.path.join(output_dir, 'financial_health.xlsx')
    df_health.to_excel(health_path, index=False, sheet_name='Health Analysis')
    print(f"  ✓ Saved: {health_path}")
    
    # 3. Export Companies Dimension
    print("\n📊 Exporting Companies Dimension...")
    df_companies = pd.read_sql('''
        SELECT 
            ticker as "Ticker",
            company_name as "Company Name",
            sector as "Sector"
        FROM silver_companies
        ORDER BY ticker
    ''', conn)
    
    companies_path = os.path.join(output_dir, 'dim_companies.xlsx')
    df_companies.to_excel(companies_path, index=False, sheet_name='Companies')
    print(f"  ✓ Saved: {companies_path}")
    
    # 4. Export Full Income Statement (Silver)
    print("\n📊 Exporting Income Statements...")
    df_income = pd.read_sql('''
        SELECT 
            s.ticker as "Ticker",
            c.company_name as "Company",
            s.fiscal_year as "Year",
            s.revenue as "Revenue",
            s.cost_of_revenue as "Cost of Revenue",
            s.gross_profit as "Gross Profit",
            s.operating_expenses as "Operating Expenses",
            s.operating_income as "Operating Income",
            s.net_income as "Net Income",
            s.ebitda as "EBITDA",
            s.eps_basic as "EPS Basic",
            s.eps_diluted as "EPS Diluted"
        FROM silver_income_statement s
        JOIN silver_companies c ON s.ticker = c.ticker
        ORDER BY s.fiscal_year DESC, s.ticker
    ''', conn)
    
    income_path = os.path.join(output_dir, 'income_statements.xlsx')
    df_income.to_excel(income_path, index=False, sheet_name='Income Statement')
    print(f"  ✓ Saved: {income_path}")
    
    # 5. Export Full Balance Sheet (Silver)
    print("\n📊 Exporting Balance Sheets...")
    df_balance = pd.read_sql('''
        SELECT 
            s.ticker as "Ticker",
            c.company_name as "Company",
            s.fiscal_year as "Year",
            s.total_assets as "Total Assets",
            s.total_liabilities as "Total Liabilities",
            s.total_equity as "Total Equity",
            s.current_assets as "Current Assets",
            s.current_liabilities as "Current Liabilities",
            s.cash_and_equivalents as "Cash & Equivalents",
            s.total_debt as "Total Debt",
            s.retained_earnings as "Retained Earnings"
        FROM silver_balance_sheet s
        JOIN silver_companies c ON s.ticker = c.ticker
        ORDER BY s.fiscal_year DESC, s.ticker
    ''', conn)
    
    balance_path = os.path.join(output_dir, 'balance_sheets.xlsx')
    df_balance.to_excel(balance_path, index=False, sheet_name='Balance Sheet')
    print(f"  ✓ Saved: {balance_path}")
    
    # 6. Export Full Cash Flow (Silver)
    print("\n📊 Exporting Cash Flow Statements...")
    df_cashflow = pd.read_sql('''
        SELECT 
            s.ticker as "Ticker",
            c.company_name as "Company",
            s.fiscal_year as "Year",
            s.operating_cash_flow as "Operating Cash Flow",
            s.investing_cash_flow as "Investing Cash Flow",
            s.financing_cash_flow as "Financing Cash Flow",
            s.free_cash_flow as "Free Cash Flow",
            s.capital_expenditures as "Capital Expenditures",
            s.dividends_paid as "Dividends Paid",
            s.net_change_in_cash as "Net Change in Cash"
        FROM silver_cash_flow s
        JOIN silver_companies c ON s.ticker = c.ticker
        ORDER BY s.fiscal_year DESC, s.ticker
    ''', conn)
    
    cashflow_path = os.path.join(output_dir, 'cash_flow_statements.xlsx')
    df_cashflow.to_excel(cashflow_path, index=False, sheet_name='Cash Flow')
    print(f"  ✓ Saved: {cashflow_path}")
    
    # 7. Create Master Excel with all sheets
    print("\n📊 Creating Master Excel File...")
    master_path = os.path.join(output_dir, 'MASTER_financial_data.xlsx')
    
    with pd.ExcelWriter(master_path, engine='openpyxl') as writer:
        df_kpi.to_excel(writer, sheet_name='KPI Dashboard', index=False)
        df_health.to_excel(writer, sheet_name='Health Analysis', index=False)
        df_income.to_excel(writer, sheet_name='Income Statement', index=False)
        df_balance.to_excel(writer, sheet_name='Balance Sheet', index=False)
        df_cashflow.to_excel(writer, sheet_name='Cash Flow', index=False)
        df_companies.to_excel(writer, sheet_name='Companies', index=False)
    
    print(f"  ✓ Saved: {master_path}")
    
    # 8. Export individual company files to EMPRESAS folder
    print("\n📊 Exporting individual company files...")
    for ticker, company_name in TECH_COMPANIES.items():
        company_folder = os.path.join(EMPRESAS_DIR, f"{ticker}_{company_name.replace(' ', '_').replace('.', '')}")
        os.makedirs(company_folder, exist_ok=True)
        
        # Filter data for this company
        company_kpi = df_kpi[df_kpi['Ticker'] == ticker]
        company_income = df_income[df_income['Ticker'] == ticker]
        company_balance = df_balance[df_balance['Ticker'] == ticker]
        company_cashflow = df_cashflow[df_cashflow['Ticker'] == ticker]
        company_health = df_health[df_health['Ticker'] == ticker]
        
        # Save individual files
        if not company_income.empty:
            company_income.to_excel(os.path.join(company_folder, 'income_statement.xlsx'), index=False)
        if not company_balance.empty:
            company_balance.to_excel(os.path.join(company_folder, 'balance_sheet.xlsx'), index=False)
        if not company_cashflow.empty:
            company_cashflow.to_excel(os.path.join(company_folder, 'cash_flow.xlsx'), index=False)
        if not company_health.empty:
            company_health.to_excel(os.path.join(company_folder, 'financial_health.xlsx'), index=False)
        
        print(f"  ✓ {ticker}: Exported to {company_folder}")
    
    conn.close()
    
    print("\n" + "=" * 60)
    print("Export complete!")
    print(f"\nFicheiros prontos para Power BI em: {output_dir}")
    print(f"Ficheiros por empresa em: {EMPRESAS_DIR}")
    print("=" * 60)


if __name__ == '__main__':
    export_to_excel()
