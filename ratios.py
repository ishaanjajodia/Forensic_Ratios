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
