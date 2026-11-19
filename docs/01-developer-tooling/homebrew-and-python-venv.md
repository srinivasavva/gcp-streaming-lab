# Homebrew & Python Virtual Environments (`venv`)

## 1. Homebrew (`brew`)
- **What it is:** The standard package manager for macOS (analogous to `apt` on Linux or internal package repositories). It installs, updates, and removes command-line developer tools cleanly inside `/opt/homebrew`.
- **Why we use it:** macOS ships with outdated system versions of Python and Git. Installing via Homebrew keeps our developer tools modern, Apple-Silicon-native, and isolated from macOS system files.
- **Key Commands Used:**
  - `brew install python@3.11 git gh` — Installs standard CLI tools.
  - `brew install --cask gcloud-cli` — Installs multi-binary SDK toolkits (`gcloud`, `bq`, `gsutil`).

## 2. Python Virtual Environments (`venv`)
- **What it is:** An isolated directory inside a project folder that holds a private Python interpreter and project-specific libraries.
- **Why we use it:** Installing packages globally causes dependency conflicts between projects. Every Python repository uses its own `venv` (never committed to Git via `.gitignore`).
- **Key Commands:**
  - `python3.11 -m venv venv` — Creates the isolated environment folder.
  - `source venv/bin/activate` — Activates the environment in the current terminal session.
