"""
Interactive Financial Health Dashboard (Cloud Version)
Streamlit-based dashboard for analyzing company financial health
Adapted for Streamlit Cloud deployment using Excel files
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os

# Page configuration
st.set_page_config(
    page_title="Financial Health Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1E3A5F;
        text-align: center;
        margin-bottom: 1rem;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
    }
    .health-excellent { background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%); }
    .health-good { background: linear-gradient(135deg, #56ab2f 0%, #a8e063 100%); }
    .health-fair { background: linear-gradient(135deg, #f2994a 0%, #f2c94c 100%); }
    .health-concerning { background: linear-gradient(135deg, #eb5757 0%, #f2994a 100%); }
    .health-poor { background: linear-gradient(135deg, #c31432 0%, #240b36 100%); }
    .info-box {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 10px;
        border-left: 4px solid #1E3A5F;
    }
</style>
""", unsafe_allow_html=True)

# Get base path for data files
BASE_PATH = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(BASE_PATH, 'data', 'gold', 'excel_export')


@st.cache_data(ttl=300)
def load_companies():
    """Load list of companies from Excel"""
    df = pd.read_excel(os.path.join(DATA_PATH, 'dim_companies.xlsx'))
    df.columns = ['ticker', 'company_name', 'sector']
    return df.sort_values('ticker')


@st.cache_data(ttl=300)
def load_kpi_data():
    """Load KPI dashboard data from Excel"""
    df = pd.read_excel(os.path.join(DATA_PATH, 'kpi_dashboard.xlsx'))
    # Rename columns to match expected format
    df.columns = ['ticker', 'company_name', 'fiscal_year', 'revenue', 'revenue_growth', 
                  'net_income', 'profit_growth', 'total_assets', 'total_debt', 'free_cash_flow',
                  'current_ratio', 'debt_to_equity', 'net_margin', 'roe', 'health_score',
                  'health_status', 'revenue_rank', 'profit_rank', 'health_rank']
    return df.sort_values(['ticker', 'fiscal_year'], ascending=[True, False])


@st.cache_data(ttl=300)
def load_health_data():
    """Load financial health data from Excel"""
    df = pd.read_excel(os.path.join(DATA_PATH, 'financial_health.xlsx'))
    # Rename columns to match expected format
    df.columns = ['ticker', 'company_name', 'fiscal_year', 'current_ratio', 'quick_ratio',
                  'cash_ratio', 'gross_margin', 'operating_margin', 'net_margin', 'roe', 'roa',
                  'debt_to_equity', 'debt_to_assets', 'asset_turnover', 'operating_cash_flow_ratio',
                  'free_cash_flow_margin', 'health_score', 'health_status', 'analysis_notes']
    return df.sort_values(['ticker', 'fiscal_year'], ascending=[True, False])


def get_health_color(status):
    """Return color based on health status"""
    colors = {
        'Excellent': '#38ef7d',
        'Good': '#a8e063',
        'Fair': '#f2c94c',
        'Concerning': '#eb5757',
        'Poor': '#c31432',
        'Unknown': '#888888'
    }
    return colors.get(status, '#888888')


def get_health_emoji(status):
    """Return emoji based on health status"""
    emojis = {
        'Excellent': '🌟',
        'Good': '✅',
        'Fair': '⚠️',
        'Concerning': '🔶',
        'Poor': '🔴',
        'Unknown': '❓'
    }
    return emojis.get(status, '❓')


def format_large_number(num):
    """Format large numbers for display"""
    if num is None:
        return "N/A"
    if pd.isna(num):
        return "N/A"
    if abs(num) >= 1e12:
        return f"${num/1e12:.2f}T"
    if abs(num) >= 1e9:
        return f"${num/1e9:.2f}B"
    if abs(num) >= 1e6:
        return f"${num/1e6:.2f}M"
    return f"${num:,.0f}"


def format_percentage(num):
    """Format percentage for display"""
    if num is None:
        return "N/A"
    if pd.isna(num):
        return None
    return f"{num*100:.1f}%"


def create_gauge_chart(value, title, max_val=100):
    """Create a gauge chart for scores"""
    if value is None:
        value = 0
    
    # Determine color based on value
    if value >= 80:
        color = "#38ef7d"
    elif value >= 65:
        color = "#a8e063"
    elif value >= 50:
        color = "#f2c94c"
    elif value >= 35:
        color = "#eb5757"
    else:
        color = "#c31432"
    
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=value,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': title, 'font': {'size': 16}},
        gauge={
            'axis': {'range': [0, max_val], 'tickwidth': 1},
            'bar': {'color': color},
            'bgcolor': "white",
            'borderwidth': 2,
            'bordercolor': "gray",
            'steps': [
                {'range': [0, 35], 'color': '#ffebee'},
                {'range': [35, 50], 'color': '#fff3e0'},
                {'range': [50, 65], 'color': '#fffde7'},
                {'range': [65, 80], 'color': '#e8f5e9'},
                {'range': [80, 100], 'color': '#e0f2f1'}
            ],
            'threshold': {
                'line': {'color': "black", 'width': 4},
                'thickness': 0.75,
                'value': value
            }
        }
    ))
    
    fig.update_layout(
        height=250,
        margin=dict(l=20, r=20, t=50, b=20)
    )
    
    return fig


def create_trend_chart(df, ticker, metric, title, format_func=None):
    """Create line chart for trends"""
    company_data = df[df['ticker'] == ticker].sort_values('fiscal_year')
    
    if company_data.empty or metric not in company_data.columns:
        return None
    
    fig = go.Figure()
    
    y_values = company_data[metric].tolist()
    
    fig.add_trace(go.Scatter(
        x=company_data['fiscal_year'],
        y=y_values,
        mode='lines+markers+text',
        line=dict(color='#667eea', width=3),
        marker=dict(size=10),
        text=[format_func(v) if format_func else f"{v:.2f}" for v in y_values],
        textposition='top center'
    ))
    
    fig.update_layout(
        title=title,
        xaxis_title="Year",
        yaxis_title="",
        height=300,
        margin=dict(l=20, r=20, t=50, b=20)
    )
    
    return fig


def explain_health_status(health_row):
    """Generate detailed explanation of health status"""
    
    # Liquidity Analysis
    st.subheader("💧 Liquidity Analysis")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        cr = health_row.get('current_ratio')
        if cr is not None and not pd.isna(cr):
            if cr >= 2.0:
                st.success(f"**Current Ratio: {cr:.2f}**\n\nExcellent! The company can cover short-term debts 2x over.")
            elif cr >= 1.5:
                st.success(f"**Current Ratio: {cr:.2f}**\n\nGood liquidity position.")
            elif cr >= 1.0:
                st.warning(f"**Current Ratio: {cr:.2f}**\n\nAdequate, but limited safety margin.")
            else:
                st.error(f"**Current Ratio: {cr:.2f}**\n\n⚠️ May struggle to pay short-term obligations!")
    
    with col2:
        cash_r = health_row.get('cash_ratio')
        if cash_r is not None and not pd.isna(cash_r):
            if cash_r >= 0.5:
                st.success(f"**Cash Ratio: {cash_r:.2f}**\n\nStrong cash position.")
            elif cash_r >= 0.25:
                st.info(f"**Cash Ratio: {cash_r:.2f}**\n\nAdequate cash reserves.")
            else:
                st.warning(f"**Cash Ratio: {cash_r:.2f}**\n\nLimited immediate liquidity.")
    
    with col3:
        qr = health_row.get('quick_ratio')
        if qr is not None and not pd.isna(qr):
            if qr >= 1.0:
                st.success(f"**Quick Ratio: {qr:.2f}**\n\nCan meet obligations without selling inventory.")
            else:
                st.warning(f"**Quick Ratio: {qr:.2f}**\n\nMay need to liquidate inventory.")
    
    # Profitability Analysis
    st.subheader("💰 Profitability Analysis")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        gm = health_row.get('gross_margin')
        if gm is not None and not pd.isna(gm):
            gm_pct = gm * 100
            if gm >= 0.4:
                st.success(f"**Gross Margin: {gm_pct:.1f}%**\n\nExcellent pricing power and cost control.")
            elif gm >= 0.25:
                st.success(f"**Gross Margin: {gm_pct:.1f}%**\n\nHealthy gross margins.")
            elif gm >= 0.15:
                st.warning(f"**Gross Margin: {gm_pct:.1f}%**\n\nThin margins, competitive pressure.")
            else:
                st.error(f"**Gross Margin: {gm_pct:.1f}%**\n\n⚠️ Very low margins!")
    
    with col2:
        nm = health_row.get('net_margin')
        if nm is not None and not pd.isna(nm):
            nm_pct = nm * 100
            if nm >= 0.20:
                st.success(f"**Net Margin: {nm_pct:.1f}%**\n\nExcellent profitability!")
            elif nm >= 0.10:
                st.success(f"**Net Margin: {nm_pct:.1f}%**\n\nGood profit generation.")
            elif nm >= 0.05:
                st.info(f"**Net Margin: {nm_pct:.1f}%**\n\nModerate profitability.")
            elif nm >= 0:
                st.warning(f"**Net Margin: {nm_pct:.1f}%**\n\nLow profitability.")
            else:
                st.error(f"**Net Margin: {nm_pct:.1f}%**\n\n🔴 Company is losing money!")
    
    with col3:
        roe = health_row.get('roe')
        if roe is not None and not pd.isna(roe):
            roe_pct = roe * 100
            if roe >= 0.25:
                st.success(f"**ROE: {roe_pct:.1f}%**\n\nOutstanding return on shareholder equity!")
            elif roe >= 0.15:
                st.success(f"**ROE: {roe_pct:.1f}%**\n\nGood returns for shareholders.")
            elif roe >= 0.08:
                st.info(f"**ROE: {roe_pct:.1f}%**\n\nModerate returns.")
            elif roe >= 0:
                st.warning(f"**ROE: {roe_pct:.1f}%**\n\nWeak returns.")
            else:
                st.error(f"**ROE: {roe_pct:.1f}%**\n\n🔴 Negative returns!")
    
    # Leverage Analysis
    st.subheader("⚖️ Leverage & Debt Analysis")
    col1, col2 = st.columns(2)
    
    with col1:
        de = health_row.get('debt_to_equity')
        if de is not None and not pd.isna(de):
            if de <= 0.5:
                st.success(f"**Debt-to-Equity: {de:.2f}**\n\nConservative debt levels. Low financial risk.")
            elif de <= 1.0:
                st.success(f"**Debt-to-Equity: {de:.2f}**\n\nBalanced capital structure.")
            elif de <= 2.0:
                st.warning(f"**Debt-to-Equity: {de:.2f}**\n\nModerately leveraged.")
            else:
                st.error(f"**Debt-to-Equity: {de:.2f}**\n\n⚠️ High leverage! Financial risk elevated.")
    
    with col2:
        da = health_row.get('debt_to_assets')
        if da is not None and not pd.isna(da):
            da_pct = da * 100
            if da <= 0.3:
                st.success(f"**Debt-to-Assets: {da_pct:.1f}%**\n\nLow debt burden.")
            elif da <= 0.5:
                st.info(f"**Debt-to-Assets: {da_pct:.1f}%**\n\nModerate debt levels.")
            elif da <= 0.7:
                st.warning(f"**Debt-to-Assets: {da_pct:.1f}%**\n\nSignificant debt exposure.")
            else:
                st.error(f"**Debt-to-Assets: {da_pct:.1f}%**\n\n⚠️ High debt burden!")
    
    # Cash Flow Analysis
    st.subheader("💵 Cash Flow Analysis")
    col1, col2 = st.columns(2)
    
    with col1:
        ocf = health_row.get('operating_cash_flow_ratio')
        if ocf is not None and not pd.isna(ocf):
            if ocf >= 1.0:
                st.success(f"**Operating CF Ratio: {ocf:.2f}**\n\nStrong cash generation from operations.")
            elif ocf >= 0.5:
                st.info(f"**Operating CF Ratio: {ocf:.2f}**\n\nAdequate operational cash flow.")
            else:
                st.warning(f"**Operating CF Ratio: {ocf:.2f}**\n\nWeak cash generation.")
    
    with col2:
        fcf = health_row.get('free_cash_flow_margin')
        if fcf is not None and not pd.isna(fcf):
            fcf_pct = fcf * 100
            if fcf >= 0.15:
                st.success(f"**FCF Margin: {fcf_pct:.1f}%**\n\nExcellent free cash flow generation!")
            elif fcf >= 0.08:
                st.success(f"**FCF Margin: {fcf_pct:.1f}%**\n\nGood cash flow conversion.")
            elif fcf >= 0:
                st.info(f"**FCF Margin: {fcf_pct:.1f}%**\n\nPositive but limited free cash flow.")
            else:
                st.error(f"**FCF Margin: {fcf_pct:.1f}%**\n\n⚠️ Negative free cash flow!")


def main():
    """Main dashboard function"""
    
    # Header
    st.markdown('<p class="main-header">📊 Corporate Financial Health Dashboard</p>', unsafe_allow_html=True)
    st.markdown("---")
    
    # Info box for new users
    with st.expander("ℹ️ **How to use this dashboard** (Click to expand)", expanded=False):
        st.markdown("""
        ### Welcome! 👋
        
        This dashboard helps you analyze the **financial health** of top tech companies.
        
        **Steps to use:**
        1. **Select a company** from the sidebar dropdown
        2. **View the Health Score** (0-100) - higher is better
        3. **Explore the metrics** to understand WHY the company is healthy (or not)
        4. **Check trends** to see how the company has evolved over time
        
        **Health Score Interpretation:**
        - 🌟 **80-100 (Excellent)**: Strong financial position, low risk
        - ✅ **65-79 (Good)**: Healthy finances with minor concerns
        - ⚠️ **50-64 (Fair)**: Some areas need attention
        - 🔶 **35-49 (Concerning)**: Multiple warning signs
        - 🔴 **0-34 (Poor)**: Serious financial difficulties
        
        **Key Metrics Explained:**
        - **Liquidity Ratios**: Can the company pay short-term debts?
        - **Profitability Ratios**: Is the company making money?
        - **Leverage Ratios**: How much debt does the company have?
        - **Cash Flow Ratios**: Is the company generating cash?
        """)
    
    # Load data
    try:
        companies = load_companies()
        kpi_data = load_kpi_data()
        health_data = load_health_data()
    except Exception as e:
        st.error(f"❌ Error loading data: {e}")
        st.info("Make sure the Excel files exist in data/gold/excel_export/")
        return
    
    if companies.empty:
        st.warning("No data available. Please check the data files.")
        return
    
    # Sidebar - Company Selection
    st.sidebar.header("🔍 Select Company")
    
    company_options = {f"{row['ticker']} - {row['company_name']}": row['ticker'] 
                       for _, row in companies.iterrows()}
    
    selected_display = st.sidebar.selectbox(
        "Choose a company to analyze:",
        options=list(company_options.keys()),
        index=0
    )
    
    selected_ticker = company_options[selected_display]
    
    # Filter data for selected company
    company_kpi = kpi_data[kpi_data['ticker'] == selected_ticker].sort_values('fiscal_year', ascending=False)
    company_health = health_data[health_data['ticker'] == selected_ticker].sort_values('fiscal_year', ascending=False)
    
    if company_kpi.empty or company_health.empty:
        st.warning(f"No data available for {selected_ticker}")
        return
    
    # Get latest data
    latest_kpi = company_kpi.iloc[0]
    latest_health = company_health.iloc[0]
    
    # Company Header
    company_name = latest_kpi['company_name']
    health_status = latest_health['health_status']
    health_score = latest_health['health_score']
    
    st.header(f"{company_name} ({selected_ticker})")
    
    # Main metrics row
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        emoji = get_health_emoji(health_status)
        color = get_health_color(health_status)
        st.markdown(f"""
        <div style="background: {color}; padding: 1rem; border-radius: 10px; text-align: center;">
            <h2 style="color: white; margin: 0;">{emoji} {health_status}</h2>
            <p style="color: white; margin: 0;">Health Status</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        revenue_growth = latest_kpi['revenue_growth']
        revenue_delta = format_percentage(revenue_growth) if revenue_growth and not pd.isna(revenue_growth) else None
        st.metric(
            "💰 Revenue",
            format_large_number(latest_kpi['revenue']),
            revenue_delta
        )
    
    with col3:
        profit_growth = latest_kpi['profit_growth']
        profit_delta = format_percentage(profit_growth) if profit_growth and not pd.isna(profit_growth) else None
        st.metric(
            "📈 Net Income",
            format_large_number(latest_kpi['net_income']),
            profit_delta
        )
    
    with col4:
        st.metric(
            "🏦 Total Assets",
            format_large_number(latest_kpi['total_assets'])
        )
    
    st.markdown("---")
    
    # Health Score Gauge
    col1, col2 = st.columns([1, 2])
    
    with col1:
        gauge_fig = create_gauge_chart(health_score, "Financial Health Score")
        st.plotly_chart(gauge_fig, use_container_width=True)
        
        # Analysis notes
        if latest_health['analysis_notes'] and not pd.isna(latest_health['analysis_notes']):
            st.markdown("### 📝 Key Insights")
            notes = str(latest_health['analysis_notes']).split('; ')
            for note in notes:
                st.markdown(f"- {note}")
    
    with col2:
        st.markdown("### 📊 Key Financial Ratios")
        
        # Create ratio comparison chart with proper normalization
        ratio_cols = ['current_ratio', 'net_margin', 'roe', 'debt_to_equity']
        ratio_names = ['Current Ratio', 'Net Margin', 'ROE', 'Debt/Equity']
        ratio_benchmarks = {
            'current_ratio': 3.0,
            'net_margin': 0.5,
            'roe': 0.5,
            'debt_to_equity': 3.0
        }
        
        bar_data = []
        for col, name in zip(ratio_cols, ratio_names):
            val = latest_health[col] if col in latest_health else None
            if val is not None and not pd.isna(val):
                if col == 'debt_to_equity':
                    color = '#38ef7d' if val <= 1.0 else '#eb5757'
                elif col == 'current_ratio':
                    color = '#38ef7d' if val >= 1.5 else '#eb5757'
                else:
                    color = '#38ef7d' if val >= 0.1 else '#eb5757'
                
                benchmark = ratio_benchmarks[col]
                normalized_val = min((val / benchmark) * 100, 100)
                
                bar_data.append({
                    'name': name,
                    'value': normalized_val,
                    'actual': val,
                    'color': color
                })
        
        if bar_data:
            fig = go.Figure()
            for item in bar_data:
                fig.add_trace(go.Bar(
                    x=[item['name']], 
                    y=[item['value']], 
                    marker_color=item['color'], 
                    showlegend=False,
                    text=[f"{item['actual']:.2f}"], 
                    textposition='outside',
                    hovertemplate=f"{item['name']}: {item['actual']:.2f}<extra></extra>"
                ))
            
            fig.update_layout(
                height=300, 
                margin=dict(l=20, r=20, t=50, b=20),
                yaxis=dict(
                    range=[0, 110],
                    title="Normalized Score",
                    showticklabels=False
                ),
                xaxis_title=""
            )
            st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    
    # Detailed Analysis Section
    st.header("🔍 Detailed Analysis")
    
    explain_health_status(latest_health.to_dict())
    
    st.markdown("---")
    
    # Historical Trends
    st.header("📈 Historical Trends")
    
    tab1, tab2, tab3, tab4 = st.tabs(["Revenue & Profit", "Health Score", "Margins", "Leverage"])
    
    with tab1:
        col1, col2 = st.columns(2)
        with col1:
            fig = create_trend_chart(kpi_data, selected_ticker, 'revenue', 'Revenue Over Time', format_large_number)
            if fig:
                st.plotly_chart(fig, use_container_width=True)
        with col2:
            fig = create_trend_chart(kpi_data, selected_ticker, 'net_income', 'Net Income Over Time', format_large_number)
            if fig:
                st.plotly_chart(fig, use_container_width=True)
    
    with tab2:
        fig = create_trend_chart(health_data, selected_ticker, 'health_score', 'Health Score Evolution')
        if fig:
            st.plotly_chart(fig, use_container_width=True)
    
    with tab3:
        col1, col2 = st.columns(2)
        with col1:
            fig = create_trend_chart(health_data, selected_ticker, 'gross_margin', 'Gross Margin Trend', format_percentage)
            if fig:
                st.plotly_chart(fig, use_container_width=True)
        with col2:
            fig = create_trend_chart(health_data, selected_ticker, 'net_margin', 'Net Margin Trend', format_percentage)
            if fig:
                st.plotly_chart(fig, use_container_width=True)
    
    with tab4:
        col1, col2 = st.columns(2)
        with col1:
            fig = create_trend_chart(health_data, selected_ticker, 'debt_to_equity', 'Debt-to-Equity Trend')
            if fig:
                st.plotly_chart(fig, use_container_width=True)
        with col2:
            fig = create_trend_chart(health_data, selected_ticker, 'current_ratio', 'Current Ratio Trend')
            if fig:
                st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    
    # Company Comparison
    st.header("🏆 Company Ranking (Latest Year)")
    
    latest_year = kpi_data['fiscal_year'].max()
    year_data = kpi_data[kpi_data['fiscal_year'] == latest_year].copy()
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.subheader("By Revenue")
        rev_sorted = year_data.nsmallest(10, 'revenue_rank')[['ticker', 'company_name', 'revenue', 'revenue_rank']]
        rev_sorted['revenue_fmt'] = rev_sorted['revenue'].apply(format_large_number)
        
        fig = px.bar(rev_sorted, x='ticker', y='revenue', 
                     color='ticker', 
                     color_discrete_sequence=px.colors.qualitative.Set2,
                     text='revenue_fmt')
        fig.update_traces(textposition='outside')
        fig.update_layout(showlegend=False, height=400)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("By Net Income")
        profit_sorted = year_data.nsmallest(10, 'profit_rank')[['ticker', 'company_name', 'net_income', 'profit_rank']]
        profit_sorted['income_fmt'] = profit_sorted['net_income'].apply(format_large_number)
        
        fig = px.bar(profit_sorted, x='ticker', y='net_income',
                     color='ticker',
                     color_discrete_sequence=px.colors.qualitative.Set2,
                     text='income_fmt')
        fig.update_traces(textposition='outside')
        fig.update_layout(showlegend=False, height=400)
        st.plotly_chart(fig, use_container_width=True)
    
    with col3:
        st.subheader("By Health Score")
        health_year = health_data[health_data['fiscal_year'] == latest_year].copy()
        health_sorted = health_year.nlargest(10, 'health_score')[['ticker', 'company_name', 'health_score', 'health_status']]
        
        fig = px.bar(health_sorted, x='ticker', y='health_score',
                     color='health_status',
                     color_discrete_map={
                         'Excellent': '#38ef7d',
                         'Good': '#a8e063',
                         'Fair': '#f2c94c',
                         'Concerning': '#eb5757',
                         'Poor': '#c31432'
                     },
                     text='health_score')
        fig.update_traces(textposition='outside')
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #666;">
        <p>📊 Financial Health Dashboard | Universidade de Coimbra - FEUC | Built with Streamlit</p>
        <p><small>💡 Tip: Use the sidebar to switch between companies</small></p>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
