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

def calculate_piotroski_f_score(annuals):
    def safe_div(a, b):
        return a / b if b else 0

    years = []
    net_income = []
    cfo = []
    total_assets = []
    total_assets_beg = []
    revenue = []
    gross_profit = []
    long_term_debt = []
    current_assets = []
    current_liabilities = []
    shares_outstanding = []

    for i, entry in enumerate(annuals):
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

    # Total assets beginning of year
    total_assets_beg = [total_assets[0]] + total_assets[:-1]

    results = []
    for i in range(len(years)):
        fscore = 0
        criteria = []

        # 1. ROA > 0
        roa = safe_div(net_income[i], total_assets_beg[i])
        crit1 = roa > 0
        fscore += int(crit1)
        criteria.append(crit1)

        # 2. CFO > 0
        cfroa = safe_div(cfo[i], total_assets_beg[i])
        crit2 = cfroa > 0
        fscore += int(crit2)
        criteria.append(crit2)

        # 3. ROA increase
        if i > 0:
            roa_prev = safe_div(net_income[i-1], total_assets_beg[i-1])
            crit3 = roa > roa_prev
        else:
            crit3 = False
        fscore += int(crit3)
        criteria.append(crit3)

        # 4. Accruals: CFO > Net Income
        crit4 = cfo[i] > net_income[i]
        fscore += int(crit4)
        criteria.append(crit4)

        # 5. Leverage ↓
        if i > 0:
            avg_assets = (total_assets[i] + total_assets[i-1]) / 2
            avg_assets_prev = (total_assets[i-1] + total_assets[i-2]) / 2 if i > 1 else avg_assets
            gearing = safe_div(long_term_debt[i], avg_assets)
            gearing_prev = safe_div(long_term_debt[i-1], avg_assets_prev)
            crit5 = gearing < gearing_prev
        else:
            crit5 = False
        fscore += int(crit5)
        criteria.append(crit5)

        # 6. Current Ratio ↑
        if i > 0:
            curr_ratio = safe_div(current_assets[i], current_liabilities[i])
            curr_ratio_prev = safe_div(current_assets[i-1], current_liabilities[i-1])
            crit6 = curr_ratio > curr_ratio_prev
        else:
            crit6 = False
        fscore += int(crit6)
        criteria.append(crit6)

        # 7. No new shares
        if i > 0:
            crit7 = shares_outstanding[i] <= shares_outstanding[i-1]
        else:
            crit7 = True
        fscore += int(crit7)
        criteria.append(crit7)

        # 8. Gross Margin ↑
        if i > 0:
            gm = safe_div(gross_profit[i], revenue[i])
            gm_prev = safe_div(gross_profit[i-1], revenue[i-1])
            crit8 = gm > gm_prev
        else:
            crit8 = False
        fscore += int(crit8)
        criteria.append(crit8)

        # 9. Asset Turnover ↑
        if i > 0:
            at = safe_div(revenue[i], total_assets_beg[i])
            at_prev = safe_div(revenue[i-1], total_assets_beg[i-1])
            crit9 = at > at_prev
        else:
            crit9 = False
        fscore += int(crit9)
        criteria.append(crit9)

        results.append({
            'Year': years[i],
            'F-Score': fscore,
            'Criteria': criteria
        })

    return results


def calculate_montier_c_score(data):
    def safe_float(val):
        try:
            return float(val)
        except:
            return 0.0

    def get_value(section, key):
        return safe_float(next((item["value"] for item in section if item["key"] == key), 0))

    # Filter and sort annual data
    financials = [f for f in data['financials'] if f['Type'] == 'Annual']
    financials.sort(key=lambda x: int(x['FiscalYear']))

    records = []
    for entry in financials:
        year = int(entry['FiscalYear'])
        inc = entry['stockFinancialMap']['INC']
        cas = entry['stockFinancialMap']['CAS']
        bal = entry['stockFinancialMap']['BAL']

        records.append({
            "year": year,
            "net_income": get_value(inc, "NetIncome"),
            "cash_from_operations": get_value(cas, "CashfromOperatingActivities"),
            "receivables": get_value(bal, "AccountsReceivable-TradeNet"),
            "revenue": get_value(inc, "TotalRevenue"),
            "inventory": get_value(bal, "TotalInventory"),
            "cost_of_goods_sold": get_value(inc, "CostofRevenueTotal"),
            "other_current_assets": get_value(bal, "OtherCurrentAssetsTotal"),
            "gross_ppe": get_value(bal, "Property/Plant/EquipmentTotal-Net"),
            "depreciation": get_value(inc, "Depreciation/Amortization"),
            "total_assets": get_value(bal, "TotalAssets"),
        })

    results = []

    for i in range(1, len(records)):
        curr = records[i]
        prev = records[i - 1]
        score = 0
        result = {"Year": curr["year"]}

        # C1: NI/CFO increasing
        ni_cfo_prev = safe_float(prev["net_income"]) / safe_float(prev["cash_from_operations"]) if prev["cash_from_operations"] else 0
        ni_cfo_curr = safe_float(curr["net_income"]) / safe_float(curr["cash_from_operations"]) if curr["cash_from_operations"] else 0
        crit1 = ni_cfo_curr > ni_cfo_prev
        score += int(crit1)
        result["C1: NI/CFO ↑"] = "🟢" if crit1 else "❌"

        # C2: DSO ↑
        dso_prev = safe_float(prev["receivables"]) / (safe_float(prev["revenue"]) / 365) if prev["revenue"] else 0
        dso_curr = safe_float(curr["receivables"]) / (safe_float(curr["revenue"]) / 365) if curr["revenue"] else 0
        crit2 = dso_curr > dso_prev
        score += int(crit2)
        result["C2: DSO ↑"] = "🟢" if crit2 else "❌"

        # C3: DSI ↑
        dsi_prev = safe_float(prev["inventory"]) / (safe_float(prev["cost_of_goods_sold"]) / 365) if prev["cost_of_goods_sold"] else 0
        dsi_curr = safe_float(curr["inventory"]) / (safe_float(curr["cost_of_goods_sold"]) / 365) if curr["cost_of_goods_sold"] else 0
        crit3 = dsi_curr > dsi_prev
        score += int(crit3)
        result["C3: DSI ↑"] = "🟢" if crit3 else "❌"

        # C4: OCA/Revenue ↑
        oca_rev_prev = safe_float(prev["other_current_assets"]) / safe_float(prev["revenue"]) if prev["revenue"] else 0
        oca_rev_curr = safe_float(curr["other_current_assets"]) / safe_float(curr["revenue"]) if curr["revenue"] else 0
        crit4 = oca_rev_curr > oca_rev_prev
        score += int(crit4)
        result["C4: OCA/Rev ↑"] = "🟢" if crit4 else "❌"

        # C5: Dep/PPE ↓
        dep_ppe_prev = safe_float(prev["depreciation"]) / safe_float(prev["gross_ppe"]) if prev["gross_ppe"] else 0
        dep_ppe_curr = safe_float(curr["depreciation"]) / safe_float(curr["gross_ppe"]) if curr["gross_ppe"] else 0
        crit5 = dep_ppe_curr < dep_ppe_prev
        score += int(crit5)
        result["C5: Dep/PPE ↓"] = "🟢" if crit5 else "❌"

        # C6: Asset Growth > 10%
        if i >= 3:
            ta_now = safe_float(records[i]["total_assets"])
            ta_3y_back = safe_float(records[i - 3]["total_assets"])
            cagr = (ta_now / ta_3y_back) ** (1/3) - 1 if ta_3y_back else 0
            crit6 = cagr > 0.10
            score += int(crit6)
            result["C6: Asset Growth >10%"] = "🟢" if crit6 else "❌"
        else:
            result["C6: Asset Growth >10%"] = "NA"

        result["C-Score"] = f"{score}/6"
        results.append(result)

    return results
