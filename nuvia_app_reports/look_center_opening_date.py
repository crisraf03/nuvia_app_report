import pandas as pd
import nuvia 

year , month = 2023,12

name_excel = f'data\{year}\{month}\week_.xlsx'
data_ = nuvia.create_caracteristics(pd.read_excel(name_excel))


min_invoice = data_.groupby('center')['invoice'].min().to_frame().reset_index()
min_invoice['opening date'] = min_invoice['invoice'].map(data_.set_index('invoice')['date_In'])
print(min_invoice)
min_invoice.to_excel('results/opening_date.xlsx' , index=False)







