import os
import time
import threading
from werkzeug.serving import make_server
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC

from app import create_app
from config import Config

evidence_dir = os.path.abspath('execution_evidence')
os.makedirs(evidence_dir, exist_ok=True)

app = create_app(Config)
server = make_server('127.0.0.1', 5000, app)
t = threading.Thread(target=server.serve_forever, daemon=True)
t.start()
time.sleep(1.5)

opts = Options()
opts.add_argument('--headless=new')
opts.add_argument('--window-size=1366,768')
opts.add_argument('--no-sandbox')
opts.add_argument('--disable-gpu')
driver = webdriver.Chrome(options=opts)
wait = WebDriverWait(driver, 10)
base_url = 'http://127.0.0.1:5000'

print('Capturing actual screenshots from running application...')

# 1. Main Dashboard
driver.get(f'{base_url}/')
time.sleep(1)
driver.save_screenshot(os.path.join(evidence_dir, '02_main_dashboard.png'))
print('Captured: 02_main_dashboard.png')

# 2. Machine List showing 40 machines & status
driver.get(f'{base_url}/machines/')
time.sleep(1)
driver.save_screenshot(os.path.join(evidence_dir, '03_machine_list.png'))
print('Captured: 03_machine_list.png')

# 3. Machine details
driver.get(f'{base_url}/machines/M-001')
time.sleep(1)
driver.save_screenshot(os.path.join(evidence_dir, '03b_machine_details.png'))
print('Captured: 03b_machine_details.png')

# 4. STOP Operation Form
driver.get(f'{base_url}/downtime/start?machine_id=M-001')
reason_el = wait.until(EC.presence_of_element_located((By.NAME, 'reason')))
reason_el.clear()
reason_el.send_keys('Spindle motor overheating - Thermal cutoff trip')
time.sleep(1)
driver.save_screenshot(os.path.join(evidence_dir, '04_stop_operation_form.png'))
print('Captured: 04_stop_operation_form.png')

# Submit STOP
driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
time.sleep(1)

# 5. Downtime Reason & Timestamp recording (History page showing active open log)
driver.get(f'{base_url}/downtime/history')
time.sleep(1)
driver.save_screenshot(os.path.join(evidence_dir, '06_downtime_reason_and_timestamp.png'))
print('Captured: 06_downtime_reason_and_timestamp.png')

# 6. Dashboard showing stopped machine & RESUME action available
driver.get(f'{base_url}/')
time.sleep(1)
driver.save_screenshot(os.path.join(evidence_dir, '05_resume_action_available.png'))
print('Captured: 05_resume_action_available.png')

# Resume machine M-001
resume_btn = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "form.resume-form button")))
resume_btn.click()
try:
    driver.switch_to.alert.accept()
except Exception:
    pass
time.sleep(1)

# 7. Downtime Duration and Cost Calculation (History with closed event)
driver.get(f'{base_url}/downtime/history')
time.sleep(1)
driver.save_screenshot(os.path.join(evidence_dir, '07_duration_and_cost_calculation.png'))
print('Captured: 07_duration_and_cost_calculation.png')

# 8. Downtime History with Filters applied
driver.get(f'{base_url}/downtime/history')
sel = Select(driver.find_element(By.ID, 'machine_id'))
sel.select_by_value('M-001')
driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
time.sleep(1)
driver.save_screenshot(os.path.join(evidence_dir, '09_downtime_history_filtered.png'))
print('Captured: 09_downtime_history_filtered.png')

# 9. Report Generation (Pareto analysis & Rs. 50,000/hr breakdown)
driver.get(f'{base_url}/reports/')
time.sleep(1)
driver.save_screenshot(os.path.join(evidence_dir, '10_downtime_reports.png'))
print('Captured: 10_downtime_reports.png')

# 10. Simulator Console (Machine Simulator Web Interface)
driver.get(f'{base_url}/simulator')
time.sleep(1)
driver.save_screenshot(os.path.join(evidence_dir, '08_simulator_console.png'))
print('Captured: 08_simulator_console.png')

# 11. Work Orders roster
driver.get(f'{base_url}/work-orders/')
time.sleep(1)
driver.save_screenshot(os.path.join(evidence_dir, '11_work_orders.png'))
print('Captured: 11_work_orders.png')

# 12. Input Validation & Error Handling
driver.get(f'{base_url}/downtime/start')
driver.execute_script("document.getElementById('reason').removeAttribute('required'); document.getElementById('machine_id').removeAttribute('required');")
driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
time.sleep(1)
driver.save_screenshot(os.path.join(evidence_dir, '13_input_validation_error.png'))
print('Captured: 13_input_validation_error.png')

driver.quit()
server.shutdown()
print('All application screenshots captured successfully!')
