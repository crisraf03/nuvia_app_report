import pandas as pd
import nuvia


# Set the maximum date for the report and the month to add
year = 2024
month_to_add_at_the_report = 5

max_date_of_the_report = '2024-06-01'

# Define file path and name for the Excel file
name_excel = f"data\checkIn_all.xlsx"

# Read existing data from the Excel file
data_ = pd.read_excel(name_excel)

# Read additional data to add to the report
data_to_add = pd.read_excel(f"data\{year}\{month_to_add_at_the_report}\week_.xlsx")
data_to_add = data_to_add[~data_to_add['invoice'].isin(data_['invoice'])]
data_ = pd.concat([data_, data_to_add], axis=0)

# Perform additional data processing
data_ = nuvia.create_caracteristics(data_)
data_ = nuvia.create_month_year_column(data_)

# Define weeks for reporting
import accounting
weeks_ = accounting.dates_old + accounting.dates

# Calculate PMMA monthly data by week
pmma_monthly_by_week = nuvia.calculate_waiting_for_24z(data_, weeks_)
