# Git & GitHub Workflow (Mapped to Google Internal Stack)

## 1. Concept Translation
| Google Internal Tool | External Git / GitHub Equivalent | Purpose |
| :--- | :--- | :--- |
| **Piper** (central monorepo) | **GitHub Repository** | Cloud-hosted source of truth for code and docs. |
| **CitC Workspace** | **Local Git Clone + Working Tree** | Local directory where files are edited. |
| **Creating a CL** (`hg change`) | `git checkout -b <branch-name>` | Isolated branch for new features or fixes. |
| **Uploading snapshot** (`hg upload`) | `git add .` -> `git commit` -> `git push` | Stages changes, records a local commit, and pushes to GitHub. |
| **Critique** | **Pull Request (PR)** | Peer review and automated CI checks before merging into `main`. |

## 2. Authentication (`gh` vs. `gcloud`)
- `gh auth login` — Authenticates both `gh` and `git` with GitHub securely via browser OAuth (stored in macOS Keychain).
- `gcloud auth login` — Authenticates human CLI commands (`gcloud`, `bq`).
- `gcloud auth application-default login` — Saves local Application Default Credentials (ADC) so Python SDKs authenticate automatically without hardcoded service account JSON keys.

## 3. Daily 3-Command Save Workflow
```bash
git add .
git commit -m "Describe what changed"
git push
