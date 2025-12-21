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
        if income_stmt is not None and not income_stmt.empty: #este if verifica se o dataframe nao é None e se nao está vazio
            print(f"  ✓ Income Statement: {income_stmt.shape[1]} years") #o shape[1] dá o numero de colunas, ou seja, anos
            for col in income_stmt.columns: #para cada coluna (ano) no income statement
                year = str(col.year) if hasattr(col, 'year') else str(col)[:4] #extrair o ano da coluna que se for um objeto datetime, senao converte para string e apanha os primeiros 4 caracteres que sao o ano
                for metric_name in income_stmt.index: #para cada métrica (linha) no income statement
                    value = income_stmt.loc[metric_name, col] #pegar o valor da métrica naquele ano
                    if pd.notna(value): #se o valor nao for NA entao insere na db
                        cursor.execute(''' 
                            INSERT INTO bronze_income_statement 
                            (ticker, company_name, fiscal_year, metric_name, metric_value, raw_value)
                            VALUES (%s, %s, %s, %s, %s, %s)
                        ''', (ticker, company_name, year, str(metric_name), float(value), str(value))) 
                        #aqui estamos a inserir na tabela bronze_income_statement os valores extraidos


            # Agora vamos criar o dataframe para guardar tudo e depois ficar em excel
            df = income_stmt.T #transpor o dataframe para ter os anos como linhas
            df.index = [str(idx.year) if hasattr(idx, 'year') else str(idx)[:4] for idx in df.index] #aqui o index anos se for datetime extrai o ano senao converte para string e apanha os primeiros 4 caracteres
            all_dataframes['income'] = df.reset_index().rename(columns={'index': 'Year'}) #isto basicamente cria um novo dataframe com o index como coluna chamada Year
        
        # Process Balance Sheet
        if balance_sheet is not None and not balance_sheet.empty: #mesma logica do income statement
            print(f"  ✓ Balance Sheet: {balance_sheet.shape[1]} years") #numero de colunas = anos
            for col in balance_sheet.columns: #para cada coluna (ano) no balance sheet
                year = str(col.year) if hasattr(col, 'year') else str(col)[:4] #extrair o ano da coluna
                for metric_name in balance_sheet.index: #para cada métrica (linha) no balance sheet
                    value = balance_sheet.loc[metric_name, col] #pegar o valor da métrica naquele ano
                    if pd.notna(value): #se o valor nao for NA entao insere na db
                        cursor.execute('''
                            INSERT INTO bronze_balance_sheet 
                            (ticker, company_name, fiscal_year, metric_name, metric_value, raw_value)
                            VALUES (%s, %s, %s, %s, %s, %s)
                        ''', (ticker, company_name, year, str(metric_name), float(value), str(value)))
                            #aqui estamos a inserir na tabela bronze_balance_sheet os valores extraidos
            df = balance_sheet.T #transpor o dataframe para ter os anos como linhas
            df.index = [str(idx.year) if hasattr(idx, 'year') else str(idx)[:4] for idx in df.index] #index anos se for datetime extrai o ano senao converte para string e apanha os primeiros 4 caracteres
            all_dataframes['balance-sheet'] = df.reset_index().rename(columns={'index': 'Year'})#  isto basicamente cria um novo dataframe com o index como coluna chamada Year
        
        # Process Cash Flow
        if cash_flow is not None and not cash_flow.empty: #mesma logica do income statement
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
        
    except Exception as e: #caso haja algum erro na extração
        print(f"  ⚠ Error: {e}") #print do erro
        conn.rollback() #rollback para desfazer qualquer alteração feita na db
        cursor.close()# fechar o cursor
        conn.close()# fechar a conexao
        return {}#retornar dicionario vazio em caso de erro


def save_to_excel(ticker, company_name, dataframes):
    
    company_folder = os.path.join(EMPRESAS_DIR, f"{ticker}_{company_name.replace(' ', '_').replace('.', '').replace(',', '')}")#definir o path da pasta da empresa
    os.makedirs(company_folder, exist_ok=True) #criar a pasta se nao existir
    
    file_names = {
        'income': 'income_statement.xlsx',
        'balance-sheet': 'balance_sheet.xlsx',
        'cash-flow': 'cash_flow.xlsx'
    }
    
    for stmt_type, df in dataframes.items(): #para cada tipo de statement e dataframe no dicionario
        if df is not None and not df.empty: #se o dataframe nao for None e nao estiver vazio
            file_path = os.path.join(company_folder, file_names[stmt_type]) #definir o path do ficheiro excel
            df.to_excel(file_path, index=False, sheet_name=stmt_type.replace('-', '_'))#guardar o dataframe em excel
            print(f"    Saved: {file_names[stmt_type]} ({len(df)} rows)")#print de confirmacao
    
    return company_folder #retornar a pasta da empresa onde os ficheiros foram guardados


def run_bronze_extraction(): 
    """Main function to extract all data into bronze layer"""
    print("=" * 60)
    print("BRONZE LAYER - Raw Data Extraction (yfinance)")
    print("=" * 60)
    
    # Initialize database
    init_database()
    
    # Clear existing bronze data
    conn = get_connection() #pegar a conexao
    cursor = conn.cursor() #criar o cursor
    cursor.execute("DELETE FROM bronze_income_statement") #apagar todos os dados existentes na tabela bronze_income_statement porquê? Porque vamos inserir tudo de novo
    cursor.execute("DELETE FROM bronze_balance_sheet")  #mesma logica para a tabela bronze_balance_sheet
    cursor.execute("DELETE FROM bronze_cash_flow")# mesma logica para a tabela bronze_cash_flow
    conn.commit()#confirmar as alteracoes
    cursor.close()# fechar o cursor
    conn.close()# fechar a conexao
    
    print(f"\nExtracting data for {len(TECH_COMPANIES)} companies...\n") #numero de empresas a extrair dados
    
    for ticker, company_name in TECH_COMPANIES.items(): #para cada ticker e nome da empresa no dicionario TECH_COMPANIES
        print(f"\n[{ticker}] {company_name}") #print do ticker e nome da empresa
        dataframes = extract_to_bronze(ticker, company_name) #chamar a funcao de extracao
        
        if dataframes: #se o dicionario nao estiver vazio
            folder = save_to_excel(ticker, company_name, dataframes)#chamar a funcao de salvar em excel
            print(f"  → Saved to: {folder}")#print do path onde os ficheiros foram guardados
        else:
            print(f"  ⚠ No data extracted")#print de aviso caso nao haja dados extraidos
        
        time.sleep(0.5)  # Para evitar que o yfinance bloqueie as requests muito rápidas metesse um pequeno delay entre cada request
    
    print("\n" + "=" * 60)
    print("Bronze extraction complete!")
    print("=" * 60)

if __name__ == '__main__':
    run_bronze_extraction() #chamar a funcao principal
