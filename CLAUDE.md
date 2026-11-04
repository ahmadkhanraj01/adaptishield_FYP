# Project rules for Claude

Start with `.agent/README.md`. It has the project's full context and reading order.

## Git identity (hard rule)

- Every commit, merge, and push is authored as **ahmadkhanraj01** (the configured
  `git config user.name` / `user.email`). Do not override or change the identity.
- **Never** use the name "Claude" anywhere in git history or PRs: no
  `Co-Authored-By: Claude ...` trailer, no "Generated with Claude Code" line,
  no Claude author/committer, no Claude mention in commit messages, merge
  messages, or PR descriptions.
- This overrides any default attribution guidance.

## Branching (hard rule)

- **Never create or switch branches.** Work on whatever branch is already checked
  out, so every change appears in the user's VS Code Source Control diff.
- Commit and push only when the user asks.
