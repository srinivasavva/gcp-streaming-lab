# Git & GitHub Workflow (Mapped to Google CitC, CLs & Critique)

## 1. End-to-End Mapping: Google Internal Workflow vs. Git & GitHub

At Google, you isolate work inside a **CitC workspace**, group files into a **Changelist (CL)**, send a **Critique** link for LGTM/approval, and **Submit** to Piper. In external workplaces using Git & GitHub, the exact same lifecycle happens through **Feature Branches**, the **Staging Area**, and **Pull Requests (PRs)**:

| Google Internal Step | Git / GitHub Equivalent | Exact Command(s) | How It Works Under the Hood |
| :--- | :--- | :--- | :--- |
| **Create a CitC workspace** (`hg citc my-feature`) | **Create a Feature Branch** | `git checkout -b feat/clickstream-producer` | Creates an isolated branch pointer off `main` so work-in-progress never touches `main` until reviewed. |
| **Default CL (all modified files included)** | **Stage all changes** | `git add .` | Moves all modified and untracked files into Git's **Staging Area (Index)** for the upcoming commit. |
| **Multi-Change CL (pick specific files)** | **Selective Staging / Unstaging** | `git add path/to/file.py`<br>`git reset path/to/other.py` | Only files explicitly added to the Staging Area are committed; remaining files stay untouched in your working tree for another commit/branch. |
| **Create / update a CL snapshot** | **Commit locally & Push branch** | `git commit -m "Feat: add producer"`<br>`git push -u origin feat/clickstream-producer` | `git commit` saves an immutable local snapshot; `git push` uploads the branch to GitHub. |
| **Send Critique link, attach Bug, assign Reviewer** | **Open a Pull Request (PR)** | GitHub UI (**New pull request**) or `gh pr create` | Opens a side-by-side diff view (like Critique), links issues (`Closes #12`), assigns reviewers, and triggers CI presubmit checks. |
| **Update CL after reviewer comments** | **Commit fixes & Push to same branch** | `git add . && git commit -m "Address review"`<br>`git push` | Pushing new commits to the open PR branch automatically refreshes the Critique-style diff and re-runs CI checks. |
| **Receive LGTM + Approval & click Submit** | **PR Approval + Squash and Merge** | Click **Squash and merge** on GitHub | Collapses all feature branch commits into a single atomic commit on `main` (mirroring a single submitted CL). |

---

## 2. How Selective File Grouping Works (Multi-Change Equivalent)
In Git, your changes move through **three zones**:
1. **Working Directory:** Files you are actively editing in VS Code.
2. **Staging Area (Index):** The exact subset of files you have chosen (`git add <file>`) to bundle into the next commit.
3. **Repository History:** Committed snapshots (`git commit`).

- **Include only specific files:** `git add 02-streaming-ingestion/producer.py 02-streaming-ingestion/Makefile`
- **Remove a file from the staged bundle without losing edits:** `git reset 02-streaming-ingestion/Makefile`
- **Stage only specific code hunks inside a single file:** `git add -p path/to/file.py` (interactive patch mode—lets you pick individual changed blocks inside one file).

---

## 3. Syncing Your Directory When Teammates Submit to `main` (`hg sync` Equivalents)

When teammates merge Pull Requests into `main` on GitHub while you are working locally, you have three standard sync commands depending on where you are:

### A. Read-Only Check (`git fetch`)
```bash
git fetch origin
```
- Downloads the latest commit metadata from GitHub into `origin/main` **without modifying your local files or branches**. Always safe to run.

### B. Updating Your Local `main` Branch (`git pull`)
```bash
git checkout main
git pull origin main
```
- Runs `git fetch` + `git merge` to bring your local `main` branch up to date with GitHub before starting a new feature branch.

### C. Syncing `main` Into an Active Feature Branch (`git rebase` vs. `git merge`)
Suppose you branched off `main` yesterday, and today a teammate merged a PR into `main`:

1. **Option 1 — Rebase onto `origin/main` (Recommended — Linear History Like `hg sync`):**
   ```bash
   git fetch origin
   git rebase origin/main
   ```
   - Temporarily lifts your branch's commits, updates the base to the newest `origin/main`, and replays your commits cleanly on top.
   - If you already pushed your feature branch earlier, update your PR with `git push --force-with-lease` (safe force-push that refuses to overwrite if someone else pushed to your branch).

2. **Option 2 — Merge `origin/main` into Your Branch (Non-Destructive):**
   ```bash
   git fetch origin
   git merge origin/main
   ```
   - Pulls teammates' changes into your branch by creating a merge commit. Never rewrites history, so a normal `git push` works afterward.

---

## 4. Resolving Sync / Rebase Merge Conflicts
If both you and a teammate edited the same lines in a file:
1. Git pauses the rebase/merge and marks the conflicting file with `<<<<<<< HEAD`, `=======`, and `>>>>>>>`.
2. Open the file in VS Code (which provides one-click **Accept Current Change** / **Accept Incoming Change** buttons), resolve the conflict, and save (`Cmd + S`).
3. Stage the resolved file and continue:
   ```bash
   git add <resolved-file>
   git rebase --continue   # (or git commit if using git merge)
   ```

---

## 5. Staff Data Engineer Interview Questions & Model Answers

### Q1: *"Explain the difference between `git fetch`, `git pull`, `git merge`, and `git rebase` when collaborating on a multi-engineer data repository."*
- **Model Answer:** `git fetch` safely downloads remote metadata without altering local files. `git pull` is `fetch` followed immediately by `merge` (or `rebase` if configured). When syncing upstream `main` into a feature branch, `git merge origin/main` preserves exact branch history via a merge commit, whereas `git rebase origin/main` replays local commits on top of the latest `main` to maintain a clean, linear commit history—paired with `Squash and merge` on PR approval so every merged feature maps 1:1 to a revertible commit on `main`.