"""
GOLD LAYER - Create business-ready KPIs and analytics
This script calculates financial ratios and creates dashboard-ready data
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database import get_connection
from config import TECH_COMPANIES


def safe_divide(numerator, denominator):
    """Safely divide two numbers, returning None if division is not possible"""
    if numerator is None or denominator is None or denominator == 0:
        return None
    return numerator / denominator


def calculate_health_score(ratios):
    """
    Calculate a composite financial health score (0-100)
    Based on weighted scoring of key financial metrics
    """
    score = 0 # initial score
    max_score = 0 # maximum possible score
    
    # Liquidity (20 points max)
    if ratios.get('current_ratio') is not None: #verificar se o ratio existe 
        max_score += 10 # adicionar 10 ao max score
        cr = ratios['current_ratio'] #pegar o valor do current ratio, cr significa current ratio
        if cr >= 2.0:
            score += 10
        elif cr >= 1.5:
            score += 8
        elif cr >= 1.0:
            score += 5
        elif cr >= 0.5:
            score += 2
    
    if ratios.get('cash_ratio') is not None:
        max_score += 10
        cash_r = ratios['cash_ratio']
        if cash_r >= 0.5:
            score += 10
        elif cash_r >= 0.25:
            score += 7
        elif cash_r >= 0.1:
            score += 4
    
    # Profitability (30 points max)
    if ratios.get('net_margin') is not None:
        max_score += 15
        nm = ratios['net_margin']
        if nm >= 0.20:
            score += 15
        elif nm >= 0.10:
            score += 12
        elif nm >= 0.05:
            score += 8
        elif nm >= 0:
            score += 4
    
    if ratios.get('roe') is not None:
        max_score += 15
        roe = ratios['roe']
        if roe >= 0.20:
            score += 15
        elif roe >= 0.15:
            score += 12
        elif roe >= 0.10:
            score += 8
        elif roe >= 0:
            score += 4
    
    # Leverage (25 points max)
    if ratios.get('debt_to_equity') is not None:
        max_score += 15
        de = ratios['debt_to_equity']
        if de <= 0.5:
            score += 15
        elif de <= 1.0:
            score += 12
        elif de <= 2.0:
            score += 8
        elif de <= 3.0:
            score += 4
    
    if ratios.get('debt_to_assets') is not None:
        max_score += 10
        da = ratios['debt_to_assets']
        if da <= 0.3:
            score += 10
        elif da <= 0.5:
            score += 7
        elif da <= 0.7:
            score += 4
    
    # Cash Flow (25 points max)
    if ratios.get('operating_cash_flow_ratio') is not None:
        max_score += 15
        ocf = ratios['operating_cash_flow_ratio']
        if ocf >= 1.0:
            score += 15
        elif ocf >= 0.5:
            score += 10
        elif ocf >= 0.2:
            score += 5
    
    if ratios.get('free_cash_flow_margin') is not None:
        max_score += 10
        fcf = ratios['free_cash_flow_margin']
        if fcf >= 0.15:
            score += 10
        elif fcf >= 0.10:
            score += 7
        elif fcf >= 0.05:
            score += 4
        elif fcf >= 0:
            score += 2
    
    # Normalize to 0-100 scale
    if max_score > 0:
        return round((score / max_score) * 100, 2)
    return None


def get_health_status(score):
    """Convert health score to status label"""
    if score is None:
        return 'Unknown'
    if score >= 80:
        return 'Excellent'
    if score >= 65:
        return 'Good'
    if score >= 50:
        return 'Fair'
    if score >= 35:
        return 'Concerning'
    return 'Poor'


def generate_analysis_notes(ratios, score):
    """Generate textual analysis notes based on ratios"""
    notes = []
    
    if ratios.get('current_ratio'):
        cr = ratios['current_ratio']
        if cr < 1.0:
            notes.append("⚠️ Low liquidity - current ratio below 1.0")
        elif cr > 3.0:
            notes.append("💡 High liquidity - may have idle assets")
    
    if ratios.get('debt_to_equity'):
        de = ratios['debt_to_equity']
        if de > 2.0:
            notes.append("⚠️ High leverage - debt-to-equity above 2.0")
        elif de < 0.3:
            notes.append("✅ Conservative debt levels")
    
    if ratios.get('net_margin'):
        nm = ratios['net_margin']
        if nm < 0:
            notes.append("🔴 Company is not profitable")
        elif nm > 0.20:
            notes.append("✅ Excellent profit margins (>20%)")
    
    if ratios.get('roe'):
        roe = ratios['roe']
        if roe > 0.25:
            notes.append("✅ Outstanding return on equity (>25%)")
        elif roe < 0.05:
            notes.append("⚠️ Low return on equity (<5%)")
    
    if ratios.get('free_cash_flow_margin'):
        fcf = ratios['free_cash_flow_margin']
        if fcf < 0:
            notes.append("⚠️ Negative free cash flow")
        elif fcf > 0.15:
            notes.append("✅ Strong free cash flow generation")
    
    return "; ".join(notes) if notes else "No significant concerns identified."


def create_gold_layer():
    """Create gold layer analytics and KPIs"""
    print("=" * 60)
    print("GOLD LAYER - Analytics & KPI Generation")
    print("=" * 60)
    
    conn = get_connection()
    cursor = conn.cursor()
    
    # Clear existing gold data
    cursor.execute("TRUNCATE TABLE gold_financial_health CASCADE")
    cursor.execute("TRUNCATE TABLE gold_kpi_dashboard CASCADE")
    cursor.execute("TRUNCATE TABLE gold_trends CASCADE")
    conn.commit()
    
    for ticker, company_name in TECH_COMPANIES.items():
        print(f"\n[{ticker}] Calculating metrics for {company_name}...")
        
        # Get years available
        cursor.execute('''
            SELECT DISTINCT fiscal_year FROM silver_income_statement
            WHERE ticker = %s ORDER BY fiscal_year DESC
        ''', (ticker,))
        years = [row[0] for row in cursor.fetchall()]
        
        previous_revenue = None
        previous_net_income = None
        
        for year in years:
            # Get income statement data
            cursor.execute('''
                SELECT revenue, gross_profit, operating_income, net_income
                FROM silver_income_statement WHERE ticker = %s AND fiscal_year = %s
            ''', (ticker, year))
            income_row = cursor.fetchone()
            
            # Get balance sheet data
            cursor.execute('''
                SELECT total_assets, total_liabilities, total_equity, 
                       current_assets, current_liabilities, cash_and_equivalents, total_debt
                FROM silver_balance_sheet WHERE ticker = %s AND fiscal_year = %s
            ''', (ticker, year))
            balance_row = cursor.fetchone()
            
            # Get cash flow data
            cursor.execute('''
                SELECT operating_cash_flow, free_cash_flow
                FROM silver_cash_flow WHERE ticker = %s AND fiscal_year = %s
            ''', (ticker, year))
            cashflow_row = cursor.fetchone()
            
            if not income_row and not balance_row:
                continue
            
            # Extract values
            revenue = income_row[0] if income_row else None
            gross_profit = income_row[1] if income_row else None
            operating_income = income_row[2] if income_row else None
            net_income = income_row[3] if income_row else None
            
            total_assets = balance_row[0] if balance_row else None
            total_liabilities = balance_row[1] if balance_row else None
            total_equity = balance_row[2] if balance_row else None
            current_assets = balance_row[3] if balance_row else None
            current_liabilities = balance_row[4] if balance_row else None
            cash = balance_row[5] if balance_row else None
            total_debt = balance_row[6] if balance_row else None
            
            operating_cf = cashflow_row[0] if cashflow_row else None
            free_cf = cashflow_row[1] if cashflow_row else None
            
            # Calculate ratios
            ratios = {
                'current_ratio': safe_divide(current_assets, current_liabilities),
                'quick_ratio': safe_divide((current_assets or 0) - 0, current_liabilities),  # Simplified
                'cash_ratio': safe_divide(cash, current_liabilities),
                'gross_margin': safe_divide(gross_profit, revenue),
                'operating_margin': safe_divide(operating_income, revenue),
                'net_margin': safe_divide(net_income, revenue),
                'roe': safe_divide(net_income, total_equity),
                'roa': safe_divide(net_income, total_assets),
                'debt_to_equity': safe_divide(total_debt or total_liabilities, total_equity),
                'debt_to_assets': safe_divide(total_debt or total_liabilities, total_assets),
                'asset_turnover': safe_divide(revenue, total_assets),
                'operating_cash_flow_ratio': safe_divide(operating_cf, current_liabilities),
                'free_cash_flow_margin': safe_divide(free_cf, revenue),
            }
            
            # Calculate health score
            health_score = calculate_health_score(ratios)
            health_status = get_health_status(health_score)
            analysis_notes = generate_analysis_notes(ratios, health_score)
            
            # Calculate growth rates
            revenue_growth = safe_divide((revenue or 0) - (previous_revenue or 0), previous_revenue) if previous_revenue else None
            profit_growth = safe_divide((net_income or 0) - (previous_net_income or 0), abs(previous_net_income)) if previous_net_income else None
            
            # Insert into gold_financial_health
            cursor.execute('''
                INSERT INTO gold_financial_health (
                    ticker, company_name, fiscal_year,
                    current_ratio, quick_ratio, cash_ratio,
                    gross_margin, operating_margin, net_margin, roe, roa,
                    debt_to_equity, debt_to_assets, asset_turnover,
                    operating_cash_flow_ratio, free_cash_flow_margin,
                    health_score, health_status, analysis_notes
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ''', (
                ticker, company_name, year,
                ratios['current_ratio'], ratios['quick_ratio'], ratios['cash_ratio'],
                ratios['gross_margin'], ratios['operating_margin'], ratios['net_margin'],
                ratios['roe'], ratios['roa'],
                ratios['debt_to_equity'], ratios['debt_to_assets'], ratios['asset_turnover'],
                ratios['operating_cash_flow_ratio'], ratios['free_cash_flow_margin'],
                health_score, health_status, analysis_notes
            ))
            
            # Insert into gold_kpi_dashboard
            cursor.execute('''
                INSERT INTO gold_kpi_dashboard (
                    ticker, company_name, fiscal_year,
                    revenue, revenue_growth, net_income, profit_growth,
                    total_assets, total_debt, free_cash_flow,
                    current_ratio, debt_to_equity, net_margin, roe,
                    health_score, health_status
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ''', (
                ticker, company_name, year,
                revenue, revenue_growth, net_income, profit_growth,
                total_assets, total_debt or total_liabilities, free_cf,
                ratios['current_ratio'], ratios['debt_to_equity'],
                ratios['net_margin'], ratios['roe'],
                health_score, health_status
            ))
            
            # Store for next iteration (growth calculation)
            previous_revenue = revenue
            previous_net_income = net_income
        
        conn.commit()
        print(f"  ✓ Generated KPIs for {len(years)} years")
    
    # Calculate rankings
    print("\nCalculating company rankings...")
    cursor.execute('''
        UPDATE gold_kpi_dashboard d
        SET revenue_rank = sub.rev_rank,
            profit_rank = sub.profit_rank,
            health_rank = sub.health_rank
        FROM (
            SELECT id,
                   RANK() OVER (PARTITION BY fiscal_year ORDER BY revenue DESC NULLS LAST) as rev_rank,
                   RANK() OVER (PARTITION BY fiscal_year ORDER BY net_income DESC NULLS LAST) as profit_rank,
                   RANK() OVER (PARTITION BY fiscal_year ORDER BY health_score DESC NULLS LAST) as health_rank
            FROM gold_kpi_dashboard
        ) sub
        WHERE d.id = sub.id
    ''')
    conn.commit()
    
    cursor.close()
    conn.close()
    
    print("\n" + "=" * 60)
    print("Gold layer generation complete!")
    print("=" * 60)


if __name__ == '__main__':
    create_gold_layer()
