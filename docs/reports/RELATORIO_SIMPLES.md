# 📊 Relatório Simples - Análise de Empresas Tech

## O que é isto?

Este projeto vai buscar dados financeiros de **10 grandes empresas de tecnologia** (Apple, Microsoft, Google, Amazon, etc.) e analisa se estão "saudáveis" financeiramente ou não.

---

## Como funciona? (Passo a passo)

### 1️⃣ Buscar os dados

O programa vai à internet (Yahoo Finance) e descarrega os relatórios financeiros de cada empresa:

- **Income Statement** = Quanto a empresa ganhou e gastou
- **Balance Sheet** = O que a empresa tem (ativos) e deve (dívidas)
- **Cash Flow** = Quanto dinheiro entrou e saiu

### 2️⃣ Guardar numa base de dados

Os dados são guardados numa base de dados PostgreSQL, organizados em 3 camadas (como uma pirâmide):

```
      🥇 GOLD (Topo)
     Dados prontos para dashboards
     KPIs, scores, rankings

    🥈 SILVER (Meio)
    Dados limpos e organizados
    Tabelas normalizadas

  🥉 BRONZE (Base)
  Dados em bruto, tal como vieram
  Sem tratamento
```

### 3️⃣ Calcular a "saúde" da empresa

O algoritmo analisa vários indicadores:

| Indicador          | O que significa                                   |
| ------------------ | ------------------------------------------------- |
| **Current Ratio**  | A empresa consegue pagar as contas a curto prazo? |
| **Debt-to-Equity** | A empresa tem muitas dívidas?                     |
| **Net Margin**     | Quanto lucro sobra de cada € de vendas?           |
| **ROE**            | O dinheiro dos investidores está a render bem?    |
| **Free Cash Flow** | A empresa gera dinheiro "livre" para crescer?     |

### 4️⃣ Dar uma nota (0-100)

Com base nesses indicadores, cada empresa recebe:

- **80-100** = EXCELENTE 🟢
- **65-79** = BOM 🟡
- **50-64** = RAZOÁVEL 🟠
- **35-49** = PREOCUPANTE 🔴
- **0-34** = CRÍTICO ⚫

---

## Resultados obtidos

| #   | Empresa         | Nota | Estado       |
| --- | --------------- | ---- | ------------ |
| 1   | NVIDIA          | 100  | 🟢 EXCELENTE |
| 2   | Meta (Facebook) | 100  | 🟢 EXCELENTE |
| 3   | Google          | 94   | 🟢 EXCELENTE |
| 4   | Microsoft       | 88   | 🟢 EXCELENTE |
| 5   | Netflix         | 84   | 🟢 EXCELENTE |
| 6   | ASML            | 84   | 🟢 EXCELENTE |
| 7   | Apple           | 76   | 🟡 BOM       |
| 8   | Amazon          | 73   | 🟡 BOM       |
| 9   | Broadcom        | 71   | 🟡 BOM       |
| 10  | Tesla           | 59   | 🟠 RAZOÁVEL  |

**Conclusão**: Todas as 10 empresas estão saudáveis! A Tesla é a que está pior (mas ainda assim aceitável).

---

## O que foi criado?

### Pastas com ficheiros Excel

```
EMPRESAS/
├── AAPL_Apple_Inc/
│   ├── income_statement.xlsx
│   ├── balance_sheet.xlsx
│   └── cash_flow.xlsx
├── MSFT_Microsoft_Corporation/
│   └── (mesmos ficheiros)
└── ... (mais 8 empresas)
```

### Ficheiro Master para Power BI

`MASTER_financial_data.xlsx` - Tem TUDO junto, pronto para criar dashboards

### Base de dados PostgreSQL

9 tabelas organizadas com todos os dados para análises futuras

---

## Como usar para o Power BI?

1. Abre o Power BI
2. Vai a "Obter Dados" → "Excel"
3. Seleciona o ficheiro `MASTER_financial_data.xlsx`
4. Escolhe as sheets que queres (KPI Dashboard, Health Analysis, etc.)
5. Cria os teus gráficos!

**Dica**: A sheet "KPI Dashboard" já tem os dados mais importantes prontos para visualização.

---

## Empresas analisadas

1. 🍎 Apple (AAPL)
2. 🪟 Microsoft (MSFT)
3. 🔍 Alphabet/Google (GOOGL)
4. 📦 Amazon (AMZN)
5. 🎮 NVIDIA (NVDA)
6. 📘 Meta/Facebook (META)
7. 🚗 Tesla (TSLA)
8. 📡 Broadcom (AVGO)
9. 🔬 ASML (ASML)
10. 🎬 Netflix (NFLX)
