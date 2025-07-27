def calculate_sloan_ratios(data):
    results = []

    for entry in data['financials']:
        if entry['Type'] == 'Annual':
            year = entry['FiscalYear']
            net_income = next((float(item['value']) for item in entry['stockFinancialMap']['INC'] if item['key'] == 'NetIncome'), None)
            cfo = next((float(item['value']) for item in entry['stockFinancialMap']['CAS'] if item['key'] == 'CashfromOperatingActivities'), None)
            cfi = next((float(item['value']) for item in entry['stockFinancialMap']['CAS'] if item['key'] == 'CashfromInvestingActivities'), None)
            total_assets = next((float(item['value']) for item in entry['stockFinancialMap']['BAL'] if item['key'] == 'TotalAssets'), None)

            if None not in (net_income, cfo, cfi, total_assets) and total_assets != 0:
                sloan_ratio = (net_income - cfo - cfi) / total_assets
                results.append({'Year': year, 'Sloan Ratio': round(sloan_ratio, 4)})
    return results



def calculate_altman_z_scores(data):
    def safe_div(a, b):
        return a / b if b else 0

    results = []

    annual_entries = [entry for entry in data['financials'] if entry['Type'] == 'Annual']
    annual_entries.sort(key=lambda x: x.get('FiscalYear', 0))

    market_cap = float(data.get('stockDetailsReusableData', {}).get('marketCap', 0))

    def get_value(section, key):
        return float(next((v['value'] for v in section if v['key'] == key), 0))

    for entry in annual_entries:
        year = entry.get('FiscalYear', 'Unknown')
        bal = entry['stockFinancialMap']['BAL']
        inc = entry['stockFinancialMap']['INC']

        total_current_assets = get_value(bal, 'TotalCurrentAssets')
        total_current_liabilities = get_value(bal, 'TotalCurrentLiabilities')
        total_assets = get_value(bal, 'TotalAssets')
        retained_earnings = get_value(bal, 'RetainedEarnings(AccumulatedDeficit)')
        total_liabilities = get_value(bal, 'TotalLiabilities')
        revenue = get_value(inc, 'TotalRevenue')
        pretax_income = get_value(inc, 'NetIncomeBeforeTaxes')
        interest_expense = abs(get_value(inc, 'InterestInc(Exp)Net-Non-OpTotal'))
        ebit = pretax_income + interest_expense

        X1 = safe_div(total_current_assets - total_current_liabilities, total_assets)
        X2 = safe_div(retained_earnings, total_assets)
        X3 = safe_div(ebit, total_assets)
        X4 = safe_div(market_cap, total_liabilities)
        X5 = safe_div(revenue, total_assets)

        Z = 1.2 * X1 + 1.4 * X2 + 3.3 * X3 + 0.6 * X4 + 1.0 * X5

        if Z > 2.99:
            risk = "Safe zone (low risk)"
        elif Z > 1.81:
            risk = "Grey zone (moderate risk)"
        else:
            risk = "Distress zone (high risk)"

        results.append({'Year': year, 'Altman Z-Score': round(Z, 2), 'Risk Zone': risk})

    return results



import json
def safe_div(a, b):
    return a / b if b else 0
def calculate_beneish_m_score(data):
    annuals = [x for x in data['financials'] if x['Type'] == 'Annual']
    annuals = sorted(annuals, key=lambda x: int(x['FiscalYear']))

    results = []
    # Initialize arrays
    years, revenue, gross_profit, accounts_receivable, inventory = [], [], [], [], []
    current_assets, ppe, total_assets, depreciation, sgna = [], [], [], [], []
    sales, current_liabilities, long_term_debt, net_income, cfo, non_op_income = [], [], [], [], [], []

    for entry in annuals:
        years.append(entry['FiscalYear'])
        inc = entry['stockFinancialMap']['INC']
        revenue.append(float(next((v['value'] for v in inc if v['key'] == 'TotalRevenue'), 0)))
        gross_profit.append(float(next((v['value'] for v in inc if v['key'] == 'GrossProfit'), 0)))
        depreciation.append(float(next((v['value'] for v in inc if v['key'] == 'Depreciation/Amortization'), 0)))
        sgna.append(float(next((v['value'] for v in inc if v['key'] == 'Selling/General/AdminExpensesTotal'), 0)))
        net_income.append(float(next((v['value'] for v in inc if v['key'] == 'NetIncome'), 0)))
        non_op_income.append(float(next((v['value'] for v in inc if v['key'] == 'OtherNet'), 0)))
        cas = entry['stockFinancialMap']['CAS']
        cfo.append(float(next((v['value'] for v in cas if v['key'] == 'CashfromOperatingActivities'), 0)))
        bal = entry['stockFinancialMap']['BAL']
        accounts_receivable.append(float(next((v['value'] for v in bal if v['key'] == "AccountsReceivable-TradeNet"), 0)))
        inventory.append(float(next((v['value'] for v in bal if v['key'] == "TotalInventory"), 0)))
        current_assets.append(float(next((v['value'] for v in bal if v['key'] == "TotalCurrentAssets"), 0)))
        ppe.append(float(next((v['value'] for v in bal if v['key'] == "Property/Plant/EquipmentTotal-Net"), 0)))
        total_assets.append(float(next((v['value'] for v in bal if v['key'] == "TotalAssets"), 0)))
        current_liabilities.append(float(next((v['value'] for v in bal if v['key'] == "TotalCurrentLiabilities"), 0)))
        long_term_debt.append(float(next((v['value'] for v in bal if v['key'] == "LongTermDebt"), 0)))
        sales.append(float(next((v['value'] for v in inc if v['key'] == 'Revenue'), 0)))

    for i in range(1, len(years)):
        dsri = safe_div(accounts_receivable[i] / revenue[i], accounts_receivable[i-1] / revenue[i-1])
        gmi = safe_div((gross_profit[i-1] / revenue[i-1]), (gross_profit[i] / revenue[i]))
        aqi = safe_div(1 - (current_assets[i] + ppe[i]) / total_assets[i], 1 - (current_assets[i-1] + ppe[i-1]) / total_assets[i-1])
        sgi = safe_div(sales[i], sales[i-1])
        depi = safe_div(depreciation[i-1] / (depreciation[i-1] + ppe[i-1]), depreciation[i] / (depreciation[i] + ppe[i]))
        sgai = safe_div(sgna[i] / sales[i], sgna[i-1] / sales[i-1])
        lvgi = safe_div((long_term_debt[i] + current_liabilities[i]) / total_assets[i], (long_term_debt[i-1] + current_liabilities[i-1]) / total_assets[i-1])
        tata = safe_div((net_income[i] - non_op_income[i] - cfo[i]), total_assets[i])

        m_score = (
            -4.84 +
            0.92 * dsri +
            0.528 * gmi +
            0.404 * aqi +
            0.892 * sgi +
            0.115 * depi +
            0.172 * sgai -
            0.327 * lvgi +
            4.679 * tata
        )
        results.append({
            'Year': years[i],
            'Beneish M-Score': round(m_score, 2)
        })

    return results
