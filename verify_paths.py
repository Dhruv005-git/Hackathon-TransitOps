"""Verify all page CSS paths and switch_page targets are correct."""
from pathlib import Path

pages = ['1_Dashboard','2_Fleet','3_Drivers','4_Trips',
         '5_Maintenance','6_Fuel_Expenses','7_Analytics','8_Settings']

all_ok = True
for name in pages:
    page_path = Path(f'pages/{name}.py')
    css_path = page_path.parent.parent / 'frontend' / 'assets' / 'style.css'
    page_exists = page_path.exists()
    css_exists = css_path.exists()
    status = "OK" if (page_exists and css_exists) else "FAIL"
    if status == "FAIL":
        all_ok = False
    print(f"[{status}] {name}.py  page={page_exists}  css={css_exists}")

# Check app.py target
target = Path('pages/1_Dashboard.py')
print(f"\n[{'OK' if target.exists() else 'FAIL'}] app.py switch_page -> {target}")

# Check sidebar links
sidebar_path = Path('frontend/components/sidebar.py')
sidebar_text = sidebar_path.read_text(encoding='utf-8')
if '"pages/1_Dashboard"' in sidebar_text:
    print("[OK] sidebar.py uses pages/ prefix")
else:
    print("[FAIL] sidebar.py still using old path")
    all_ok = False

print()
print("ALL PATHS OK" if all_ok else "SOME PATHS FAILED - check above")
