@echo off
cd "nuvia_app_reports"
echo Select an option to execute the python3.11 file:
echo 1: lab_metric_report
echo 2: weekly_waiting_for_24z
echo 3: restorer_products
echo 4: accounting
echo 5: compare_clinic_patients
echo 6: flux_analysis
echo 7: pmma_counter
echo 8: create_caracteristics
echo 9: inventory_report
echo 10: update_checkIn_all
echo 11: fracture_report

set /p number=Enter a number (1 to 11): 

if %number% == 1 (
    echo Running lab_metric_report.py
    python3.11 lab_metric_report.py

) else if %number% == 2 (
    echo Running weekly_waiting_for_24z.py
    python3.11 weekly_waiting_for_24z.py

) else if %number% == 3 (
    echo Running restorer_products.py
    python3.11 restorer_products.py

) else if %number% == 4 (
    echo Running accounting.py
    python3.11 accounting.py

) else if %number% == 5 (
    echo Running compare_clinic_patients.py
    python3.11 compare_clinic_patients.py

) else if %number% == 6 (
    echo Running flux_analysis.py
    python3.11 flux_analysis.py

) else if %number% == 7 (
    echo Running pmma_counter.py
    python3.11 pmma_counter.py

) else if %number% == 8 (
    echo Running create_caracteristics.py
    python3.11 create_caracteristics.py

) else if %number% == 9 (
    echo Running inventory_report.py
    python3.11 inventory_report.py

) else if %number% == 10 (
    echo Running update_checkIn_all.py
    python3.11 update_checkIn_all.py

) else if %number% == 11 (
    echo Running fracture_report.py
    python3.11 fracture_report.py

) else (
    echo Invalid number. You must enter a number between 1 and 11.
)

@pause
