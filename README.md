# Road Accident Analysis — AccidentLens

A beginner-friendly Streamlit dashboard for educational road accident analysis.

## Features
- Login screen for a local classroom demo
- Accident summary metrics and filters
- Monthly, severity, location, and weather charts
- Map markers for records with valid latitude/longitude
- Add, edit, and delete accident records
- CSV import and export
- Local CSV storage in `data/accidents.csv`

## Run on Windows (VS Code)

1. Open this folder in VS Code.
2. Open **Terminal → New Terminal**.
3. Create a virtual environment:

   ```powershell
   python -m venv .venv
   ```

4. Activate it:

   ```powershell
   .\.venv\Scripts\Activate.ps1
   ```

5. Install packages:

   ```powershell
   python -m pip install --upgrade pip
   pip install -r requirements.txt
   ```

6. Start the app:

   ```powershell
   python -m streamlit run app.py
   ```

7. Open the local URL printed in the terminal, usually `http://localhost:8501`.

## Local demo login

- Username: `admin`
- Password: `ChangeMe123!`

For a local classroom demo, these defaults are convenient. Change them before sharing or deploying the app.

To set your own credentials in PowerShell for the current terminal session:

```powershell
$env:APP_USERNAME = "your_username"
$env:APP_PASSWORD = "your_strong_password"
python -m streamlit run app.py
```

## Data notes
- On first run, sample demonstration records are written to `data/accidents.csv`.
- The sample records are not official accident statistics.
- Back up the CSV before deleting or replacing data.
- Local CSV storage is not suitable for concurrent public users; use a database and production authentication for a deployed app.
