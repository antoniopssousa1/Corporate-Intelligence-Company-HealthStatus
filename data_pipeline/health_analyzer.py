"""
FINANCIAL HEALTH ANALYZER
Independent algorithm to determine if a company is financially healthy
Based on comprehensive analysis of financial statements
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database import get_connection
from config import TECH_COMPANIES


class FinancialHealthAnalyzer:
    """
    Comprehensive financial health analyzer for companies
    
    Evaluation Criteria:
    1. Liquidity - Can the company pay short-term obligations?
    2. Solvency - Can the company meet long-term obligations?
    3. Profitability - Is the company generating profits?
    4. Efficiency - How well does the company use its assets?
    5. Cash Flow - Is the company generating cash?
    6. Growth - Is the company growing?
    """
    
    # Benchmark thresholds for tech companies
    THRESHOLDS = {
        # Liquidity
        'current_ratio': {'excellent': 2.0, 'good': 1.5, 'fair': 1.0, 'poor': 0.5},
        'quick_ratio': {'excellent': 1.5, 'good': 1.0, 'fair': 0.7, 'poor': 0.3},
        'cash_ratio': {'excellent': 0.5, 'good': 0.3, 'fair': 0.15, 'poor': 0.05},
        
        # Profitability
        'gross_margin': {'excellent': 0.50, 'good': 0.35, 'fair': 0.20, 'poor': 0.10},
        'operating_margin': {'excellent': 0.25, 'good': 0.15, 'fair': 0.08, 'poor': 0.0},
        'net_margin': {'excellent': 0.20, 'good': 0.10, 'fair': 0.05, 'poor': 0.0},
        'roe': {'excellent': 0.20, 'good': 0.15, 'fair': 0.10, 'poor': 0.05},
        'roa': {'excellent': 0.15, 'good': 0.10, 'fair': 0.05, 'poor': 0.02},
        
        # Leverage (lower is better for these)
        'debt_to_equity': {'excellent': 0.5, 'good': 1.0, 'fair': 2.0, 'poor': 3.0},
        'debt_to_assets': {'excellent': 0.3, 'good': 0.5, 'fair': 0.6, 'poor': 0.7},
        
        # Cash Flow
        'operating_cash_flow_ratio': {'excellent': 1.0, 'good': 0.6, 'fair': 0.3, 'poor': 0.1},
        'free_cash_flow_margin': {'excellent': 0.15, 'good': 0.10, 'fair': 0.05, 'poor': 0.0},
    }
    
    # Weight for each category
    CATEGORY_WEIGHTS = {
        'liquidity': 0.15,
        'profitability': 0.30,
        'leverage': 0.20,
        'cash_flow': 0.20,
        'growth': 0.15
    }
    
    def __init__(self, ticker):
        self.ticker = ticker
        self.conn = get_connection()
        self.metrics = {}
        self.scores = {}
        self.overall_score = None
        self.health_status = None
        self.analysis_report = []
    
    def load_data(self):
        """Load latest financial data for the company"""
        cursor = self.conn.cursor()
        
        # Get latest year's health data
        cursor.execute('''
            SELECT 
                fiscal_year,
                current_ratio, quick_ratio, cash_ratio,
                gross_margin, operating_margin, net_margin, roe, roa,
                debt_to_equity, debt_to_assets,
                operating_cash_flow_ratio, free_cash_flow_margin
            FROM gold_financial_health
            WHERE ticker = %s
            ORDER BY fiscal_year DESC
            LIMIT 1
        ''', (self.ticker,))
        
        row = cursor.fetchone()
        if row:
            self.metrics = {
                'fiscal_year': row[0],
                'current_ratio': row[1],
                'quick_ratio': row[2],
                'cash_ratio': row[3],
                'gross_margin': row[4],
                'operating_margin': row[5],
                'net_margin': row[6],
                'roe': row[7],
                'roa': row[8],
                'debt_to_equity': row[9],
                'debt_to_assets': row[10],
                'operating_cash_flow_ratio': row[11],
                'free_cash_flow_margin': row[12]
            }
        
        # Get growth data (compare last 2 years)
        cursor.execute('''
            SELECT revenue, net_income FROM gold_kpi_dashboard
            WHERE ticker = %s
            ORDER BY fiscal_year DESC
            LIMIT 2
        ''', (self.ticker,))
        
        rows = cursor.fetchall()
        if len(rows) >= 2:
            current = rows[0]
            previous = rows[1]
            if current[0] and previous[0] and previous[0] != 0:
                self.metrics['revenue_growth'] = (current[0] - previous[0]) / abs(previous[0])
            if current[1] and previous[1] and previous[1] != 0:
                self.metrics['profit_growth'] = (current[1] - previous[1]) / abs(previous[1])
        
        cursor.close()
        return bool(self.metrics)
    
    def score_metric(self, metric_name, value, reverse=False):
        """
        Score a metric from 0-100 based on thresholds
        reverse=True for metrics where lower is better (like debt ratios)
        """
        if value is None:
            return None
        
        thresholds = self.THRESHOLDS.get(metric_name)
        if not thresholds:
            return None
        
        if reverse:
            if value <= thresholds['excellent']:
                return 100
            elif value <= thresholds['good']:
                return 75
            elif value <= thresholds['fair']:
                return 50
            elif value <= thresholds['poor']:
                return 25
            else:
                return 10
        else:
            if value >= thresholds['excellent']:
                return 100
            elif value >= thresholds['good']:
                return 75
            elif value >= thresholds['fair']:
                return 50
            elif value >= thresholds['poor']:
                return 25
            else:
                return 10
    
    def analyze_liquidity(self):
        """Analyze liquidity position"""
        scores = []
        notes = []
        
        cr = self.metrics.get('current_ratio')
        if cr is not None:
            score = self.score_metric('current_ratio', cr)
            scores.append(score)
            if cr < 1.0:
                notes.append(f"⚠️ ALERTA: Current Ratio ({cr:.2f}) abaixo de 1.0 - possíveis problemas de liquidez")
            elif cr > 3.0:
                notes.append(f"💡 Current Ratio ({cr:.2f}) muito alto - possível capital ocioso")
            else:
                notes.append(f"✅ Current Ratio ({cr:.2f}) saudável")
        
        cash_r = self.metrics.get('cash_ratio')
        if cash_r is not None:
            score = self.score_metric('cash_ratio', cash_r)
            scores.append(score)
            if cash_r < 0.1:
                notes.append(f"⚠️ Cash Ratio ({cash_r:.2f}) baixo - reservas de caixa limitadas")
        
        self.scores['liquidity'] = sum(scores) / len(scores) if scores else 0
        return scores, notes
    
    def analyze_profitability(self):
        """Analyze profitability"""
        scores = []
        notes = []
        
        for metric in ['gross_margin', 'operating_margin', 'net_margin', 'roe', 'roa']:
            value = self.metrics.get(metric)
            if value is not None:
                score = self.score_metric(metric, value)
                scores.append(score)
                
                metric_label = metric.replace('_', ' ').title()
                if value < 0:
                    notes.append(f"🔴 {metric_label}: {value*100:.1f}% - NEGATIVO")
                elif score >= 75:
                    notes.append(f"✅ {metric_label}: {value*100:.1f}% - Excelente")
                elif score <= 25:
                    notes.append(f"⚠️ {metric_label}: {value*100:.1f}% - Abaixo do ideal")
        
        self.scores['profitability'] = sum(scores) / len(scores) if scores else 0
        return scores, notes
    
    def analyze_leverage(self):
        """Analyze debt/leverage levels"""
        scores = []
        notes = []
        
        de = self.metrics.get('debt_to_equity')
        if de is not None:
            score = self.score_metric('debt_to_equity', de, reverse=True)
            scores.append(score)
            if de > 2.0:
                notes.append(f"⚠️ ALERTA: Debt-to-Equity ({de:.2f}) muito alto - empresa muito alavancada")
            elif de < 0.5:
                notes.append(f"✅ Debt-to-Equity ({de:.2f}) conservador - baixa alavancagem")
            else:
                notes.append(f"ℹ️ Debt-to-Equity ({de:.2f}) dentro de níveis aceitáveis")
        
        da = self.metrics.get('debt_to_assets')
        if da is not None:
            score = self.score_metric('debt_to_assets', da, reverse=True)
            scores.append(score)
            if da > 0.6:
                notes.append(f"⚠️ Debt-to-Assets ({da:.2f}) elevado - mais de 60% dos ativos financiados por dívida")
        
        self.scores['leverage'] = sum(scores) / len(scores) if scores else 0
        return scores, notes
    
    def analyze_cash_flow(self):
        """Analyze cash flow health"""
        scores = []
        notes = []
        
        ocf = self.metrics.get('operating_cash_flow_ratio')
        if ocf is not None:
            score = self.score_metric('operating_cash_flow_ratio', ocf)
            scores.append(score)
            if ocf < 0.3:
                notes.append(f"⚠️ Operating Cash Flow Ratio ({ocf:.2f}) baixo")
            elif ocf >= 1.0:
                notes.append(f"✅ Operating Cash Flow Ratio ({ocf:.2f}) excelente - forte geração de caixa")
        
        fcf = self.metrics.get('free_cash_flow_margin')
        if fcf is not None:
            score = self.score_metric('free_cash_flow_margin', fcf)
            scores.append(score)
            if fcf < 0:
                notes.append(f"🔴 Free Cash Flow Margin ({fcf*100:.1f}%) NEGATIVO - empresa a queimar caixa")
            elif fcf >= 0.15:
                notes.append(f"✅ Free Cash Flow Margin ({fcf*100:.1f}%) forte")
        
        self.scores['cash_flow'] = sum(scores) / len(scores) if scores else 0
        return scores, notes
    
    def analyze_growth(self):
        """Analyze growth trends"""
        scores = []
        notes = []
        
        rev_growth = self.metrics.get('revenue_growth')
        if rev_growth is not None:
            if rev_growth > 0.20:
                scores.append(100)
                notes.append(f"✅ Crescimento de receita: +{rev_growth*100:.1f}% - Excelente")
            elif rev_growth > 0.10:
                scores.append(75)
                notes.append(f"✅ Crescimento de receita: +{rev_growth*100:.1f}% - Bom")
            elif rev_growth > 0:
                scores.append(50)
                notes.append(f"ℹ️ Crescimento de receita: +{rev_growth*100:.1f}% - Moderado")
            else:
                scores.append(25)
                notes.append(f"⚠️ Receita em declínio: {rev_growth*100:.1f}%")
        
        profit_growth = self.metrics.get('profit_growth')
        if profit_growth is not None:
            if profit_growth > 0.15:
                scores.append(100)
                notes.append(f"✅ Crescimento de lucro: +{profit_growth*100:.1f}%")
            elif profit_growth > 0:
                scores.append(75)
            elif profit_growth > -0.10:
                scores.append(50)
            else:
                scores.append(25)
                notes.append(f"⚠️ Lucro em declínio: {profit_growth*100:.1f}%")
        
        self.scores['growth'] = sum(scores) / len(scores) if scores else 50  # Default to neutral
        return scores, notes
    
    def calculate_overall_score(self):
        """Calculate weighted overall health score"""
        total_score = 0
        total_weight = 0
        
        for category, weight in self.CATEGORY_WEIGHTS.items():
            if category in self.scores:
                total_score += self.scores[category] * weight
                total_weight += weight
        
        if total_weight > 0:
            self.overall_score = round(total_score / total_weight, 1)
        else:
            self.overall_score = 0
        
        # Determine health status
        if self.overall_score >= 80:
            self.health_status = "EXCELENTE"
        elif self.overall_score >= 65:
            self.health_status = "BOM"
        elif self.overall_score >= 50:
            self.health_status = "RAZOÁVEL"
        elif self.overall_score >= 35:
            self.health_status = "PREOCUPANTE"
        else:
            self.health_status = "CRÍTICO"
        
        return self.overall_score, self.health_status
    
    def run_full_analysis(self):
        """Run complete financial health analysis"""
        if not self.load_data():
            return None, "Dados não disponíveis para esta empresa"
        
        all_notes = []
        
        # Run all analyses
        _, liquidity_notes = self.analyze_liquidity()
        all_notes.extend(liquidity_notes)
        
        _, profitability_notes = self.analyze_profitability()
        all_notes.extend(profitability_notes)
        
        _, leverage_notes = self.analyze_leverage()
        all_notes.extend(leverage_notes)
        
        _, cashflow_notes = self.analyze_cash_flow()
        all_notes.extend(cashflow_notes)
        
        _, growth_notes = self.analyze_growth()
        all_notes.extend(growth_notes)
        
        # Calculate overall score
        score, status = self.calculate_overall_score()
        
        self.analysis_report = all_notes
        
        return score, status
    
    def get_report(self):
        """Generate comprehensive analysis report"""
        report = []
        report.append("=" * 70)
        report.append(f"  RELATÓRIO DE SAÚDE FINANCEIRA - {self.ticker}")
        report.append(f"  Ano Fiscal: {self.metrics.get('fiscal_year', 'N/A')}")
        report.append("=" * 70)
        report.append("")
        
        # Overall Score
        report.append(f"  📊 PONTUAÇÃO GERAL: {self.overall_score}/100")
        report.append(f"  🏥 STATUS: {self.health_status}")
        report.append("")
        
        # Category Scores
        report.append("  PONTUAÇÃO POR CATEGORIA:")
        report.append("  " + "-" * 40)
        for category, score in self.scores.items():
            bar = "█" * int(score / 10) + "░" * (10 - int(score / 10))
            report.append(f"  {category.upper():15} [{bar}] {score:.1f}")
        report.append("")
        
        # Detailed Notes
        report.append("  ANÁLISE DETALHADA:")
        report.append("  " + "-" * 40)
        for note in self.analysis_report:
            report.append(f"  {note}")
        report.append("")
        
        # Recommendation
        report.append("  RECOMENDAÇÃO:")
        report.append("  " + "-" * 40)
        if self.health_status == "EXCELENTE":
            report.append("  ✅ Empresa em excelente saúde financeira.")
            report.append("  ✅ Fundamentos sólidos em todas as áreas.")
        elif self.health_status == "BOM":
            report.append("  ✅ Empresa financeiramente saudável.")
            report.append("  ℹ️ Algumas áreas podem ser melhoradas.")
        elif self.health_status == "RAZOÁVEL":
            report.append("  ⚠️ Empresa com saúde financeira moderada.")
            report.append("  ⚠️ Requer monitorização de algumas métricas.")
        elif self.health_status == "PREOCUPANTE":
            report.append("  🔴 Empresa com sinais de stress financeiro.")
            report.append("  🔴 Recomenda-se análise mais profunda.")
        else:
            report.append("  🚨 Empresa em situação financeira crítica.")
            report.append("  🚨 Alto risco - necessita intervenção urgente.")
        
        report.append("")
        report.append("=" * 70)
        
        return "\n".join(report)
    
    def is_healthy(self):
        """Simple boolean check if company is considered healthy"""
        return self.overall_score is not None and self.overall_score >= 50
    
    def close(self):
        """Close database connection"""
        self.conn.close()


def analyze_all_companies():
    """Analyze all tech companies and generate reports"""
    print("\n" + "=" * 70)
    print("  ANÁLISE DE SAÚDE FINANCEIRA - TODAS AS EMPRESAS")
    print("=" * 70)
    
    results = []
    
    for ticker, company_name in TECH_COMPANIES.items():
        analyzer = FinancialHealthAnalyzer(ticker)
        score, status = analyzer.run_full_analysis()
        
        if score is not None:
            results.append({
                'ticker': ticker,
                'company': company_name,
                'score': score,
                'status': status,
                'healthy': analyzer.is_healthy()
            })
            
            print(analyzer.get_report())
        else:
            print(f"\n⚠️ {ticker}: {status}")
        
        analyzer.close()
    
    # Summary table
    if results:
        print("\n" + "=" * 70)
        print("  RESUMO - RANKING DE SAÚDE FINANCEIRA")
        print("=" * 70)
        print(f"\n  {'Rank':<6}{'Ticker':<8}{'Empresa':<25}{'Score':<10}{'Status':<15}{'Saudável?'}")
        print("  " + "-" * 70)
        
        results.sort(key=lambda x: x['score'], reverse=True)
        for i, r in enumerate(results, 1):
            healthy_icon = "✅" if r['healthy'] else "❌"
            print(f"  {i:<6}{r['ticker']:<8}{r['company'][:23]:<25}{r['score']:<10}{r['status']:<15}{healthy_icon}")
        
        # Statistics
        healthy_count = sum(1 for r in results if r['healthy'])
        avg_score = sum(r['score'] for r in results) / len(results)
        
        print("\n  " + "-" * 70)
        print(f"  Empresas Saudáveis: {healthy_count}/{len(results)} ({healthy_count/len(results)*100:.0f}%)")
        print(f"  Pontuação Média: {avg_score:.1f}/100")
        print("=" * 70)


def analyze_single_company(ticker):
    """Analyze a single company"""
    analyzer = FinancialHealthAnalyzer(ticker)
    score, status = analyzer.run_full_analysis()
    
    if score is not None:
        print(analyzer.get_report())
        return analyzer.is_healthy()
    else:
        print(f"Não foi possível analisar {ticker}: {status}")
        return None
    
    analyzer.close()


if __name__ == '__main__':
    import sys
    
    if len(sys.argv) > 1:
        # Analyze specific company
        ticker = sys.argv[1].upper()
        analyze_single_company(ticker)
    else:
        # Analyze all companies
        analyze_all_companies()
