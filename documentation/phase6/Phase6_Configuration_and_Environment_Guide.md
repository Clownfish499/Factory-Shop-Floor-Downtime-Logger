# Phase 6: Configuration and Environment Guide
## Case 47 – Factory Shop-Floor Execution System

---

### 1. Overview
The Factory Shop-Floor Execution System uses a layered configuration model defined in [`config.py`](file:///c:/Users/HP/OneDrive/one%20drive1/OneDrive/Desktop/sepm2/config.py) that reads from system environment variables with sensible defaults for local development.

A template configuration file is provided in [`.env.example`](file:///c:/Users/HP/OneDrive/one%20drive1/OneDrive/Desktop/sepm2/.env.example).

---

### 2. Supported Environment Variables

| Variable Name | Default Value | Description | Production Recommendation |
| :--- | :--- | :--- | :--- |
| **`FLASK_ENV`** | `development` | Operating environment mode (`development`, `production`, or `testing`). | Set to `production` to disable debug mode and suppress stack traces. |
| **`FLASK_DEBUG`** | `0` (or `1` if development) | Enables/disables Flask interactive debugger and hot reloader. | Must be set to `0` or `false` in production. |
| **`SECRET_KEY`** | `dev-secret-key-case-47-downtime-logger` | Secret key used for cryptographic session signing and CSRF protection. | Generate a strong random key: `python -c "import secrets; print(secrets.token_hex(32))"`. |
| **`DATABASE_PATH`** | `factory.db` | Relative or absolute path to persistent SQLite database file. | Set to a dedicated storage path with proper write permissions. |
| **`DOWNTIME_HOURLY_RATE`** | `50000.0` | Cost constant defined by Case 47 (Rs. 50,000 per hour). | Keep at `50000.0` for assignment fidelity. |
| **`FLASK_RUN_HOST`** | `127.0.0.1` | Network interface address for server binding. | `127.0.0.1` for local safety; `0.0.0.0` when running in Docker. |
| **`FLASK_RUN_PORT`** | `5000` | Port on which web application listens. | `5000` or standard web port (`8080`). |

---

### 3. Setting Up Local Environment

#### Windows PowerShell:
```powershell
# Set environment variables in the active PowerShell session
$env:FLASK_ENV = "development"
$env:DATABASE_PATH = "factory.db"
$env:SECRET_KEY = "your-custom-local-secret-key"

# Run the application
python app.py
```

#### Linux / macOS Bash:
```bash
export FLASK_ENV=development
export DATABASE_PATH=factory.db
export SECRET_KEY=your-custom-local-secret-key

python app.py
```

---

### 4. Configuration Classes in `config.py`

- **`DevelopmentConfig`**: Enables debug output, detailed logging, and binds to local `factory.db`.
- **`ProductionConfig`**: Disables debug mode (`DEBUG = False`), validates secret key hygiene, and ensures errors return user-friendly messages rather than stack traces.
- **`TestConfig`**: Uses in-memory or temporary disk database (`:memory:`) to guarantee total isolation from the developer's demo database.
- **`get_config(env_name)`**: Dynamic factory function selecting the appropriate configuration class automatically.

---

### 5. Logging Configuration
Application logs are configured via standard Python `logging`:
- **Format**: `%(asctime)s [%(levelname)s] %(name)s: %(message)s`
- **Levels**:
  - `DEBUG` when running under `DevelopmentConfig`.
  - `INFO` when running under `ProductionConfig`.
- **Log Sanitation**: Database queries, requests, and errors are logged without exposing passwords, secret tokens, or personal identifiers.
