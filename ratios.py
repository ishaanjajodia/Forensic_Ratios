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
                sloan_ratio = ((net_income - cfo - cfi) / total_assets) * 100
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
    'DSRI': round(dsri, 3),
    'GMI': round(gmi, 3),
    'AQI': round(aqi, 3),
    'SGI': round(sgi, 3),
    'DEPI': round(depi, 3),
    'SGAI': round(sgai, 3),
    'LVGI': round(lvgi, 3),
    'TATA': round(tata, 3),
    'Beneish M-Score': round(m_score, 2)
})


    return results






# ratios.py

def calculate_piotroski_f_score_verbose(annuals):
    def safe_div(a, b):
        return a / b if b else 0

    years = []
    net_income, cfo, total_assets, revenue, gross_profit = [], [], [], [], []
    long_term_debt, current_assets, current_liabilities, shares_outstanding = [], [], [], []

    for entry in annuals:
        years.append(entry['FiscalYear'])
        inc = entry['stockFinancialMap']['INC']
        net_income.append(float(next((v['value'] for v in inc if v['key'] == 'NetIncome'), 0)))
        revenue.append(float(next((v['value'] for v in inc if v['key'] == 'TotalRevenue'), 0)))
        gross_profit.append(float(next((v['value'] for v in inc if v['key'] == 'GrossProfit'), 0)))
        cas = entry['stockFinancialMap']['CAS']
        cfo.append(float(next((v['value'] for v in cas if v['key'] == 'CashfromOperatingActivities'), 0)))
        bal = entry['stockFinancialMap']['BAL']
        total_assets.append(float(next((v['value'] for v in bal if v['key'] == 'TotalAssets'), 0)))
        long_term_debt.append(float(next((v['value'] for v in bal if v['key'] == 'LongTermDebt'), 0)))
        current_assets.append(float(next((v['value'] for v in bal if v['key'] == 'TotalCurrentAssets'), 0)))
        current_liabilities.append(float(next((v['value'] for v in bal if v['key'] == 'TotalCurrentLiabilities'), 0)))
        shares_outstanding.append(float(next((v['value'] for v in bal if v['key'] == 'TotalCommonSharesOutstanding'), 0)))

    total_assets_beg = [total_assets[0]] + total_assets[:-1]

    for i in range(len(years)):
        print(f"\n=== Year {years[i]} ===")
        fscore = 0
        reasons = []

        # 1. ROA > 0
        roa = safe_div(net_income[i], total_assets_beg[i])
        crit1 = roa > 0
        fscore += int(crit1)
        print(f"Criterion 1 (ROA > 0): Net Income = {net_income[i]}, Total Assets Beg = {total_assets_beg[i]}")
        print(f"ROA = {roa:.4f} -> {'Yes' if crit1 else 'No'}")

        # 2. CFO > 0
        cfroa = safe_div(cfo[i], total_assets_beg[i])
        crit2 = cfroa > 0
        fscore += int(crit2)
        print(f"Criterion 2 (CFROA > 0): CFO = {cfo[i]}, Total Assets Beg = {total_assets_beg[i]}")
        print(f"CFROA = {cfroa:.4f} -> {'Yes' if crit2 else 'No'}")

        # 3. ROA increase
        if i > 0:
            roa_prev = safe_div(net_income[i - 1], total_assets_beg[i - 1])
            crit3 = roa > roa_prev
            fscore += int(crit3)
            print(f"Criterion 3 (ROA Increase): ROA = {roa:.4f}, Prev ROA = {roa_prev:.4f} -> {'Yes' if crit3 else 'No'}")
        else:
            print("Criterion 3: Skipped (no previous year)")

        # 4. CFO > Net Income
        crit4 = cfo[i] > net_income[i]
        fscore += int(crit4)
        print(f"Criterion 4 (CFO > NI): CFO = {cfo[i]}, Net Income = {net_income[i]} -> {'Yes' if crit4 else 'No'}")

        # 5. Leverage ↓
        if i > 0:
            avg_assets = (total_assets[i] + total_assets[i - 1]) / 2
            avg_assets_prev = (total_assets[i - 1] + total_assets[i - 2]) / 2 if i > 1 else avg_assets
            gearing = safe_div(long_term_debt[i], avg_assets)
            gearing_prev = safe_div(long_term_debt[i - 1], avg_assets_prev)
            crit5 = gearing < gearing_prev
            fscore += int(crit5)
            print(f"Criterion 5 (Lower Leverage): Gearing = {gearing:.4f}, Prev = {gearing_prev:.4f} -> {'Yes' if crit5 else 'No'}")
        else:
            print("Criterion 5: Skipped (no previous year)")

        # 6. Current Ratio ↑
        if i > 0:
            curr_ratio = safe_div(current_assets[i], current_liabilities[i])
            curr_ratio_prev = safe_div(current_assets[i - 1], current_liabilities[i - 1])
            crit6 = curr_ratio > curr_ratio_prev
            fscore += int(crit6)
            print(f"Criterion 6 (Current Ratio ↑): Current = {curr_ratio:.2f}, Prev = {curr_ratio_prev:.2f} -> {'Yes' if crit6 else 'No'}")
        else:
            print("Criterion 6: Skipped (no previous year)")

        # 7. No new shares issued
        if i > 0:
            crit7 = shares_outstanding[i] <= shares_outstanding[i - 1]
            fscore += int(crit7)
            print(f"Criterion 7 (No new shares): Current = {shares_outstanding[i]}, Prev = {shares_outstanding[i-1]} -> {'Yes' if crit7 else 'No'}")
        else:
            print("Criterion 7: Assumed Yes (first year)")
            fscore += 1

        # 8. Gross Margin ↑
        if i > 0:
            gm = safe_div(gross_profit[i], revenue[i])
            gm_prev = safe_div(gross_profit[i - 1], revenue[i - 1])
            crit8 = gm > gm_prev
            fscore += int(crit8)
            print(f"Criterion 8 (Gross Margin ↑): GM = {gm:.2f}, Prev = {gm_prev:.2f} -> {'Yes' if crit8 else 'No'}")
        else:
            print("Criterion 8: Skipped (no previous year)")

        # 9. Asset Turnover ↑
        if i > 0:
            at = safe_div(revenue[i], total_assets_beg[i])
            at_prev = safe_div(revenue[i - 1], total_assets_beg[i - 1])
            crit9 = at > at_prev
            fscore += int(crit9)
            print(f"Criterion 9 (Asset Turnover ↑): AT = {at:.2f}, Prev = {at_prev:.2f} -> {'Yes' if crit9 else 'No'}")
        else:
            print("Criterion 9: Skipped (no previous year)")

        print(f"🎯 F-Score: {fscore}/9")


