# Setup: venv + Git (5 commits). Run: .\setup.ps1
python -m venv .venv
.\.venv\Scripts\Activate.ps1
git init
git add anomaly-basic/main.py
git commit -m "Variant A: pressure outlier detection and series filtering"
git add .gitignore .vscode setup.ps1
git commit -m "Add .gitignore and VS Code settings"
git add anomaly-advanced
git commit -m "Variant B: Z-score and IQR detectors, median imputation"
git add exercises
git commit -m "Add exercises 1-7"
git add README.md
git commit -m "Add README with filtering formulas"
