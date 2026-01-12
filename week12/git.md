# **Git Fundamentals — Comprehensive Summary**

A complete guide to Git basics, including configuration, staging, committing, branching, remotes, pushing, pulling, resetting, restoring, and more.

---

## 1. Git Configuration

Set identity globally or locally or system-wide:

```bash
git config --global user.name "Himanshu"
git config --global user.email "himanshu@example.com"
```

View all configs:

```bash
git config --list
```

---

## 2. Creating or Initializing a Repository

Create a new repo:

```bash
git init
```

Clone an existing repo:

```bash
git clone https://github.com/user/repo.git
```

Cloning automatically sets a remote named **origin**.

---

## 3. Understanding Git Areas

```
Working Directory → Staging Area (Index) → Local Repository → Remote Repository
```

* **Working Directory:** Your actual files
* **Staging Area:** Files you have marked for next commit
* **Local Repository:** Your full history database
* **Remote Repository:** GitHub/GitLab/Bitbucket server copy

---

## 4. Adding Files (git add)

Stage changes for commit:

```bash
git add file.txt
git add src/
git add .
```

View staged/unstaged changes:

```bash
git status
```

---

## 5. Commit (git commit)

Create a snapshot of staged changes:

```bash
git commit -m "Meaningful commit message"
```

Amend the last commit:

```bash
git commit --amend
```

---

## 6. Viewing History (git log)

Basic log:

```bash
git log
```

More readable/summarized:

```bash
git log --oneline --graph --decorate --all
```

Compare with remote:

```bash
git log HEAD..origin/main
```

---

## 7. Branching

Create a branch:

```bash
git branch feature-login
```

Create + switch:

```bash
git checkout -b feature-login
```

List branches:

```bash
git branch
```

Switch branches:

```bash
git checkout main
```

Delete a branch:

```bash
git branch -d feature-login
```

---

## 8. Merging Branches

Fast-forward merge:

```bash
git checkout main
git merge feature-login
```

Normal merge (two-parent commit):

```bash
git merge feature-login
```

---

## 9. Git Reset, Restore, Revert (Differences)

These commands modify history or working directory.

---

### ### 🔹 **1. git restore**

Affects only your *working directory*.

Discard unstaged changes:

```bash
git restore file.txt
```

Restore from a specific commit:

```bash
git restore --source=<commit> file.txt
```

---

### ### 🔹 **2. git reset**

Moves branch pointer (HEAD). Can also modify staging area & working directory.

**Soft reset** (keep changes staged):

```bash
git reset --soft HEAD~1
```

**Mixed reset** (default, keep changes in working directory but unstage):

```bash
git reset HEAD~1
```

**Hard reset** (discard changes completely):

```bash
git reset --hard HEAD~1
```

⚠️ Hard reset rewrites history — dangerous if already pushed.

---

### ### 🔹 **3. git revert**

Safely undo a commit by making a new commit.

```bash
git revert <commit-hash>
```

Does NOT rewrite history — safe for shared branches.

---

## 10. Fetch, Pull, and Push

### ### 🔹 **git fetch**

Downloads new commits from remote without modifying your files.

```bash
git fetch
```

Inspect remote updates:

```bash
git log HEAD..origin/main
git diff HEAD origin/main
```

---

### ### 🔹 **git pull**

Fetch + merge:

```bash
git pull
```

Or fetch + rebase:

```bash
git pull --rebase
```

---

### ### 🔹 **git push**

Send commits to remote:

```bash
git push origin main
```

Push a new branch (first time):

```bash
git push -u origin feature-login
```

Delete remote branch:

```bash
git push origin --delete feature-login
```

---

## 11. Remotes

### ### 🔹 Add a remote

```bash
git remote add origin https://github.com/user/repo.git
```

`origin` is just a name — you choose it.

---

### ### 🔹 Remove a remote

```bash
git remote remove origin
```

This removes only the local configuration, not the remote server repo.

---

### ### 🔹 View remotes

```bash
git remote -v
```

---

### ### 🔹 Change remote URL

```bash
git remote set-url origin https://github.com/user/new-repo.git
```

---

## 12. Clone vs Pull vs Fetch (Summary)

| Command     | Purpose                                  |
| ----------- | ---------------------------------------- |
| `git clone` | First-time download of entire repository |
| `git fetch` | Download new commits (no merge)          |
| `git pull`  | Fetch + merge/rebase                     |

---

## 13. Branching & Merging Internals (Conceptual)

### Branch = pointer to a commit

```
main → C3
```

Create new branch:

```
main → C3
new-branch → C3
```

Commit on new branch:

```
main → C3
new-branch → C3 → D1
```

Merge creates a new commit if histories diverge:

```
C3 → E1 (merge commit)
 ↑     ↑
 |     |
D1     C3
```

---

## 14. Undoing Mistakes (Safe Ways)

### Undo staged file:

```bash
git reset file.txt
```

### Undo last commit but keep changes:

```bash
git reset --soft HEAD~1
```

### Undo last commit safely (new commit):

```bash
git revert HEAD
```

### Restore a deleted file:

```bash
git restore file.txt
```

---

## 15. Git Remote Workflow Summary

### Clone repo:

```bash
git clone <url>
```

### Get latest remote commits:

```bash
git fetch
```

### Update local branch with remote branch:

```bash
git pull
```

### Push local commits to remote:

```bash
git push
```

### Push a new branch:

```bash
git push -u origin newbranch
```

---

## 16. Housekeeping Commands

### View differences:

```bash
git diff
git diff --staged
```

### Delete untracked files:

```bash
git clean -f
```

### Show remote branches:

```bash
git branch -r
```

### Show all branches:

```bash
git branch -a
```

---

## 17. Highly Useful but Often Forgotten

### Show current branch tracking info:

```bash
git branch -vv
```

### Show the reflog (time machine):

```bash
git reflog
```

This helps recover lost commits after reset.

---

## Final Summary Table

| Feature               | Command                       |
| --------------------- | ----------------------------- |
| Initialize repo       | `git init`                    |
| Configure user        | `git config --global`         |
| Add changes           | `git add`                     |
| Commit                | `git commit`                  |
| View status           | `git status`                  |
| View history          | `git log`                     |
| Create branch         | `git checkout -b`             |
| Merge branch          | `git merge`                   |
| Reset soft/mixed/hard | `git reset`                   |
| Restore files         | `git restore`                 |
| Revert commit         | `git revert`                  |
| Add remote            | `git remote add`              |
| Remove remote         | `git remote remove`           |
| Push branch           | `git push -u origin <branch>` |
| Pull latest changes   | `git pull`                    |
| Fetch without merge   | `git fetch`                   |
| Clone repo            | `git clone`                   |

---
