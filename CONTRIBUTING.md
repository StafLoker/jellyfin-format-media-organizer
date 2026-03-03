# Contributing

## Language

All code, comments, docstrings, variable names, and documentation must be written in **English**. This includes commit messages, pull request titles and descriptions, and inline comments.

## Branch Strategy

| Branch       | Purpose                                           |
| ------------ | ------------------------------------------------- |
| `main`       | Production — stable, released code                |
| `develop`    | Development — integration branch for ongoing work |
| `release/v*` | Release staging — e.g. `release/v1.2.0`           |

- Feature branches are cut from `develop`: `feat/my-feature`
- Hotfix branches are cut from `main`: `hotfix/critical-bug`
- Merge `develop` → `release/v*` → `main` when releasing

## Commit Messages

Follow [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>(<scope>): <short description>
```

**Types:**

| Type       | When to use                              |
| ---------- | ---------------------------------------- |
| `feat`     | New feature                              |
| `fix`      | Bug fix                                  |
| `refactor` | Code change that is not a fix or feature |
| `chore`    | Maintenance, dependency updates, tooling |
| `docs`     | Documentation only                       |
| `test`     | Adding or updating tests                 |
| `ci`       | CI/CD pipeline changes                   |
| `perf`     | Performance improvement                  |
| `style`    | Formatting, whitespace (no logic change) |
| `revert`   | Reverting a previous commit              |

**Examples:**

```
feat(parser): add HDR token detection
fix(formatter): remove trailing dash when quality is missing
refactor(tmdb): extract search logic into separate method
chore(deps): bump uv to 0.5.0
docs(readme): add installation instructions
test(parser): add pipeline integration tests
ci: add release workflow to PyPI
```

- Use the imperative mood: "add feature" not "added feature"
- Keep the subject line under 72 characters
- Reference issues when relevant: `fix(daemon): handle missing file (#42)`

## Code Style

- **Linter/formatter:** `ruff` — run `make lint` and `make format` before committing
- **Python version:** 3.12+
- **Package manager:** `uv`

Run all checks:

```bash
make lint
make format
make test
```

## Pull Requests

- Open PRs against `develop` (or `main` for hotfixes)
- Keep PRs focused — one concern per PR
- All tests must pass before merging
- Add or update tests for any changed behaviour
