
# 🧾 Git Standards – Trunk-Based Development (POC)

This document defines consistent standards for working with Git in a trunk-based development model (as of now). It helps maintain a clean, understandable history and ensures smooth collaboration, even for small teams.

---

## 1. Branching Strategy

In trunk-based development, all work is integrated into a shared `dev` branch quickly via short-lived branches.

### Branch Naming Convention
```
<type>/<short-description>
```
**Examples:**
- `feat/user-auth`
- `fix/login-bug`
- `chore/update-readme`
- `refactor/db-schema`

### Branch Types
- `feat/`: New feature
- `fix/`: Bug fix
- `chore/`: Maintenance, config, docs
- `refactor/`: Non-functional code changes
- `test/`: Adding/updating tests
- `spike/`: Experimental work

---

## 2. Commit Message Convention

```
<type>(scope): short description
```

**Examples:**
```
feat(auth): add JWT token generation
fix(api): handle 500 error for invalid payload
chore: update dependencies
```

### Commit Types
- `feat`: A new feature
- `fix`: A bug fix
- `docs`: Documentation changes
- `style`: Formatting only (no code change)
- `refactor`: Code refactoring without behavior change
- `perf`: Performance improvement
- `test`: Adding or fixing tests
- `chore`: Non-production code (build, config, etc.)

---

## 3. Pull Request (PR) Standards

Even in trunk-based workflows, PRs help manage reviews, tests, and history.

### 🔖 PR Title Format
```
<type>(scope): short description
```
**Examples:**
- `feat(chat): integrate speech-to-text`
- `fix(frontend): remove broken mic icon`

### 📄 PR Description Template
```markdown
### Summary
Describe what this change does and why.

### Changes
- Item 1
- Item 2

### How to Test
Steps to manually test or relevant unit test info.
```

---

## 4. General Git Best Practices

- ✅ **Always pull the latest `dev` before starting a new branch**
  ```bash
  git checkout dev
  git pull origin dev
  git checkout -b feat/my-feature
  ```

- ✅ **Keep commits atomic and descriptive**
  - Don’t batch unrelated changes.
  - Avoid `WIP` or `misc` commits.
  

- ✅ **Use `rebase` instead of `merge`**
  - Keeps history linear.
  - Example:
    ```bash
    git fetch origin
    git rebase origin/dev
    ```

- ✅ **Squash commits before merging**
  - Combine multiple commits into one meaningful commit.


- ✅ **Delete branches after merging**
  ```bash
  git branch -d feat/my-feature             # Local
  git push origin --delete feat/my-feature  # Remote
  ```
  
---

## 5. Commit Squashing

Squashing combines multiple commits into one to keep the Git history clean.

### Benefits:
- Clean, meaningful commit history
- Each commit represents a complete feature or fix
- Easier code reviews and reversions

```
Before:
- feat(auth): initial token setup
- fix(auth): token refresh bug
- chore(auth): remove debug logs

After squash:
- feat(auth): implement token handling with refresh

```

## 6. Team Collaboration

- Don’t push broken code to shared branches
- Use draft PRs for early feedback
- Never force-push to `dev` or shared branches
- Use `.gitignore` to avoid committing logs, secrets, or build artifacts


---

## 📌 Appendix

### `.gitignore` Example
```
*.log
__pycache__/
.env
*.zip
.DS_Store
.vscode/
```

---