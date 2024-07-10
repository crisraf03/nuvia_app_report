import pandas as pd 

name_excel  = 'report_months.xlsx'
df_months_ = pd.read_excel(name_excel, sheet_name='report months')

# df_months_ = df_months.set_index(['center','year', 'month'])

rates = []

for center_ in df_months_['center'].unique():
    df_months  = df_months_[df_months_['center'] == center_].copy().fillna(0)
    df_months = df_months.sort_values(by=['year', 'month'], ascending=True)

    df_months['N3 total'] = df_months['N3 surgery'] + df_months['N3 redo']
    df_months['N3 rate'] = df_months['N3 total'].diff()

    df_months['N6 out'] = df_months['N6 1RX out'] + df_months['N6 +2RX out']
    df_months['N6 out rate'] = df_months['N6 out'].diff()

    df_months['N6 in'] = df_months['N6 1RX in'] + df_months['N6 +2RX in']
    df_months['N6 in rate'] = df_months['N6 in'].diff()

    rates.append(df_months)

rates = pd.concat(rates, axis=0)
rates.to_excel('rate_ns.xlsx')



