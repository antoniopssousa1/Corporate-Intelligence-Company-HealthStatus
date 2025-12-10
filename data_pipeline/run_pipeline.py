"""
MAIN PIPELINE - Run the complete ETL pipeline
Bronze -> Silver -> Gold -> Excel Export
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database import init_database
from extract_bronze import run_bronze_extraction
from transform_silver import transform_to_silver
from create_gold import create_gold_layer
from health_analyzer import analyze_all_companies
from export_excel import export_to_excel


def run_full_pipeline():
    """Execute the complete data pipeline"""
    print("\n")
    print("╔" + "═" * 68 + "╗")
    print("║" + " " * 20 + "FINANCIAL DATA PIPELINE" + " " * 25 + "║")
    print("║" + " " * 15 + "Medallion Architecture (Bronze → Silver → Gold)" + " " * 6 + "║")
    print("╚" + "═" * 68 + "╝")
    print("\n")
    
    # Step 1: Initialize Database
    print("📦 Step 1: Initializing PostgreSQL Database...")
    init_database()
    
    # Step 2: Bronze Layer - Extract raw data
    print("\n🥉 Step 2: Bronze Layer - Extracting raw data from stockanalysis.com...")
    run_bronze_extraction()
    
    # Step 3: Silver Layer - Transform and clean
    print("\n🥈 Step 3: Silver Layer - Transforming and cleaning data...")
    transform_to_silver()
    
    # Step 4: Gold Layer - Create KPIs and analytics
    print("\n🥇 Step 4: Gold Layer - Creating KPIs and analytics...")
    create_gold_layer()
    
    # Step 5: Health Analysis
    print("\n🏥 Step 5: Running Financial Health Analysis...")
    analyze_all_companies()
    
    # Step 6: Export to Excel
    print("\n📊 Step 6: Exporting to Excel for Self-Service BI...")
    export_to_excel()
    
    print("\n")
    print("╔" + "═" * 68 + "╗")
    print("║" + " " * 20 + "PIPELINE COMPLETE! ✅" + " " * 27 + "║")
    print("╚" + "═" * 68 + "╝")
    print("\n")
    print("Próximos passos:")
    print("  1. Abre o ficheiro MASTER_financial_data.xlsx no Excel")
    print("  2. Importa para o Power BI para criar dashboards")
    print("  3. Usa as tabelas gold_* para análises prontas para visualização")
    print("\n")


if __name__ == '__main__':
    run_full_pipeline()
