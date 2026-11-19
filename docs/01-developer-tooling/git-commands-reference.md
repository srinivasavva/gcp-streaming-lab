# Git Commands Reference Guide (Mapped to Google Internal Stack)

## 1. High-Level Concept Translation
- **Piper (Central Monorepo)** -> **GitHub Repository** (Cloud-hosted source of truth)
- **CitC Workspace** -> **Local Working Directory** (`~/gcp-streaming-lab` on your Mac)
- **Creating a CL (`g4 change` / `hg change`)** -> **Branching (`git checkout -b`)**
- **CL File List (`g4 opened`)** -> **Staging Area (`git add`)**
- **Uploading a CL Snapshot (`hg upload` / `g4 snapshot`)** -> **Local Commit (`git commit`) + Cloud Sync (`git push`)**
- **Critique Code Review** -> **GitHub Pull Request (PR)**
- **Submitting a CL (`g4 submit`)** -> **Merging a Pull Request into `main`**

---

## 2. Repository Setup & Cloning

- **`git init`**
  - **What it does:** Turns an ordinary folder on your Mac into a Git-tracked repository by creating a hidden `.git/` database inside it.
  - **Google Internal Equivalent:** Creating a brand-new project root inside Piper (except in Git, each project gets its own separate repository instead of one global monorepo).

- **`git clone <repo-url>`**
  - **What it does:** Downloads a complete copy of an existing GitHub repository onto your Mac so you can edit it locally.
  - **Google Internal Equivalent:** Creating a new **CitC workspace** (`g4 citc <workspace_name>`) to view and edit files from Piper on your local machine.

- **`git config --global user.name "Your Name"` & `git config --global user.email "you@example.com"`**
  - **What it does:** Stamps your name and email onto every commit you make so history shows who authored each change.
  - **Google Internal Equivalent:** Automatic via your corporate LDAP identity (`corp` login) when creating or submitting CLs.

---

## 3. Daily Save & Sync Commands (Your Core Loop)

- **`git status`**
  - **What it does:** Lists which files are brand-new (untracked), modified, or currently staged in the shopping cart ready to be committed.
  - **Google Internal Equivalent:** Running **`g4 status`** or **`hg status`** inside your CitC client to see which files you have touched.

- **`git diff`**
  - **What it does:** Displays the exact line-by-line additions (`+`) and deletions (`-`) you made since your last saved snapshot.
  - **Google Internal Equivalent:** Running **`g4 diff`** or **`hg diff`** in the terminal (or viewing the side-by-side diff inside Critique).

- **`git add <file>` (or `git add .` for all files)**
  - **What it does:** Places specific modified files into the **Staging Area** (a preparation box) to include them in your next snapshot.
  - **Google Internal Equivalent:** Attaching modified files to a specific **CL file list** (`g4 change` / `hg add`). Unlike CitC, which tracks every edited file automatically, Git ignores changes until you explicitly `git add` them.

- **`git commit -m "Clear description"`**
  - **What it does:** Takes everything currently in the Staging Area and saves a permanent, timestamped snapshot in your **local** Git history on your MacBook Air.
  - **Google Internal Equivalent:** Creating a **CL snapshot (`g4 snapshot` / `hg commit`)** with a CL description—except it is saved *only on your laptop* and is not visible on GitHub yet.

- **`git push`**
  - **What it does:** Uploads all your local `commit` snapshots from your MacBook Air up to **GitHub (`origin`)** so your cloud repository is updated and backed up.
  - **Google Internal Equivalent:** Running **`hg upload`** to push your local CitC snapshot up to Google's servers so Critique and other teammates can see it.

- **`git pull`**
  - **What it does:** Fetches the latest commits from GitHub and merges them into your local folder on your Mac.
  - **Google Internal Equivalent:** Running **`g4 sync`** or **`hg sync`** to pull the latest head changes from Piper into your CitC workspace.

---

## 4. Branching & Team Review Workflow

- **`git branch`**
  - **What it does:** Lists all local branches in your repository and puts an asterisk (`*`) next to the branch you are currently working on.
  - **Google Internal Equivalent:** Listing your active CLs / workspaces (`g4 pending` or `hg xl`).

- **`git checkout -b <branch-name>` (or `git switch -c <branch-name>`)**
  - **What it does:** Creates a brand-new isolated branch and switches your working folder into it so you can build a feature without altering `main`.
  - **Google Internal Equivalent:** Starting a **new CL (`g4 change` / `hg change`)** isolated from the main Piper trunk until it passes review and tests.

- **`git checkout main` (or `git switch main`)**
  - **What it does:** Switches your local folder back to the primary production branch (`main`).
  - **Google Internal Equivalent:** Switching back to a clean CitC client synced to Piper head (`//depot/google3/...`) with no pending CLs.

- **`git merge <branch-name>`**
  - **What it does:** Combines the commits from `<branch-name>` into your current branch (in team workflows, you open a **Pull Request** on GitHub and click **Merge** after review).
  - **Google Internal Equivalent:** Submitting an approved CL (**`g4 submit`**) after receiving LGTM in Critique and passing presubmit TAP tests.

---

## 5. History & Safe Undo Commands

- **`git log --oneline`**
  - **What it does:** Prints a clean, compact timeline of past commits (short commit ID + commit message).
  - **Google Internal Equivalent:** Viewing CL submission history in Piper / Code Search (`cs/`).

- **`git restore --staged <file>`**
  - **What it does:** Removes a file from the Staging Area if you ran `git add` by mistake, while keeping all your actual edits in the file untouched.
  - **Google Internal Equivalent:** Removing a file from a CL's file list (`g4 reopen` / moving a file back to the default changelist) without reverting your code edits.

- **`git restore <file>`**
  - **What it does:** Discards all unsaved edits in `<file>` and resets it back to how it looked at your last `git commit`.
  - **Google Internal Equivalent:** Running **`g4 revert <file>`** or **`hg revert <file>`** to throw away local CitC changes and restore the clean Piper version.

- **`git revert <commit-hash>`**
  - **What it does:** Undoes a past commit that was already pushed to GitHub by creating a *new* commit that reverses those changes cleanly without rewriting history.
  - **Google Internal Equivalent:** Rolling back a submitted CL in Piper via a **rollback CL** (`g4 rollback <CL_number>`).
