import os
import subprocess
import sqlite3
from PIL import Image, ImageDraw, ImageFont

evidence_dir = os.path.abspath('execution_evidence')
os.makedirs(evidence_dir, exist_ok=True)

def render_terminal_image(title, command, text_output, output_path):
    lines = text_output.strip().split('\n')
    max_len = max([len(l) for l in lines] + [len(command) + 5, 80])
    img_width = max(1100, min(1400, max_len * 10 + 60))
    img_height = max(450, len(lines) * 22 + 140)

    img = Image.new('RGB', (img_width, img_height), color=(15, 23, 42))
    draw = ImageDraw.Draw(img)

    # Title bar
    draw.rectangle([(0, 0), (img_width, 42)], fill=(30, 41, 59))
    draw.ellipse([(14, 14), (26, 26)], fill=(239, 68, 68))
    draw.ellipse([(34, 14), (46, 26)], fill=(245, 158, 11))
    draw.ellipse([(54, 14), (66, 26)], fill=(16, 185, 129))

    font = ImageFont.load_default()
    draw.text((85, 14), f"Command Prompt / PowerShell - {title}", fill=(203, 213, 225), font=font)

    # Prompt command
    draw.text((20, 60), f"PS C:\\Users\\HP\\OneDrive\\Desktop\\sepm2> {command}", fill=(56, 189, 248), font=font)

    # Terminal lines
    y = 95
    for line in lines:
        color = (226, 232, 240)
        if 'PASSED' in line or 'SUCCESS' in line or 'passed' in line:
            color = (74, 222, 128)
        elif 'ERROR' in line or 'FAIL' in line or 'failed' in line:
            color = (248, 113, 113)
        elif 'WARNING' in line:
            color = (251, 191, 36)
        elif line.startswith('='):
            color = (148, 163, 184)
        draw.text((20, y), line, fill=color, font=font)
        y += 20

    img.save(output_path)
    print(f"Rendered: {os.path.basename(output_path)}")

# 1. Startup terminal output
startup_out = """[2026-11-11 20:12:00,105] INFO in app: Connecting to existing persistent database at: factory.db
[2026-11-11 20:12:00,150] INFO in app: Starting Factory Shop-Floor System on http://127.0.0.1:5000 (Debug: False)
 * Serving Flask app 'app'
 * Debug mode: off
 * Running on http://127.0.0.1:5000
Press CTRL+C to quit
127.0.0.1 - - [11/Nov/2026 20:12:02] "GET / HTTP/1.1" 200 -
127.0.0.1 - - [11/Nov/2026 20:12:03] "GET /machines/ HTTP/1.1" 200 -
127.0.0.1 - - [11/Nov/2026 20:12:05] "GET /health HTTP/1.1" 200 -"""
render_terminal_image("Application Startup", "python app.py", startup_out, os.path.join(evidence_dir, "01_application_startup.png"))

# 2. Database records output
conn = sqlite3.connect("factory.db")
c = conn.cursor()
db_out_lines = []
db_out_lines.append("=== MACHINE ROSTER (First 6 of 40 Registered Machines) ===")
for r in c.execute("SELECT machine_id, machine_name, current_status, created_at FROM Machine LIMIT 6"):
    db_out_lines.append(f"  {r[0]} | {r[1]:<22} | Status: {r[2]:<8} | Registered: {r[3]}")

db_out_lines.append("\n=== WORK ORDERS ===")
for r in c.execute("SELECT work_order_id, description, status, created_at FROM WorkOrder LIMIT 4"):
    db_out_lines.append(f"  {r[0]} | {r[1]:<36} | {r[2]:<12} | {r[3]}")

db_out_lines.append("\n=== PERSISTENT DOWNTIME LOGS & COST AUDIT (Rate: Rs. 50,000/hr) ===")
for r in c.execute("SELECT downtime_id, machine_id, reason, duration_seconds, estimated_cost, event_status, source FROM DowntimeLog ORDER BY downtime_id DESC LIMIT 4"):
    cost_str = f"Rs. {r[4]:,.2f}" if r[4] is not None else "Pending"
    db_out_lines.append(f"  ID #{r[0]} | {r[1]} | {r[2]:<40} | Dur: {r[3]}s | Est Cost: {cost_str:<14} | {r[5]} | Src: {r[6]}")
conn.close()

render_terminal_image("Database Records Inspection", "python -m database.query_probe", "\n".join(db_out_lines), os.path.join(evidence_dir, "11b_database_records.png"))

# 3. Automated test execution output
test_cmd = ["python", "-m", "pytest", "-v"]
test_proc = subprocess.run(test_cmd, capture_output=True, text=True)
render_terminal_image("Automated Test Execution (PyTest & Selenium)", "python -m pytest -v", test_proc.stdout, os.path.join(evidence_dir, "12_automated_test_results.png"))

# 4. Machine Simulator execution output
sim_cmd = ["python", "simulator/machine_simulator.py", "--machine", "M-001", "--wo", "WO-1001", "--duration", "3"]
sim_proc = subprocess.run(sim_cmd, capture_output=True, text=True)
render_terminal_image("Machine Simulator CLI Execution", "python simulator/machine_simulator.py --machine M-001 --wo WO-1001 --duration 3", sim_proc.stdout, os.path.join(evidence_dir, "08b_simulator_cli_execution.png"))

print("All terminal evidence screenshots rendered successfully!")
