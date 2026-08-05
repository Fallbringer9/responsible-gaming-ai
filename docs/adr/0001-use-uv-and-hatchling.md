# ADR-0001: Use uv and Hatchling for Python Project Management

- Status: Accepted
- Date: 2026-07-16
- Decision owners: Emmanuel Oreste

## Context

Responsible Gaming AI is a new Python 3.13 project using a `src/` layout.

The project requires:

- reproducible dependency installation;
- isolated development environments;
- explicit separation between production and development dependencies;
- a lock file committed to the repository;
- standards-based package construction;
- simple local and CI commands.

The traditional Python workflow based on `venv`, `pip`, manually maintained `requirements.txt` files and `pip freeze` spreads these responsibilities across multiple commands and files.

## Decision

The project will use:

- `uv` to create and synchronize the virtual environment;
- `uv` to add, remove and lock dependencies;
- `uv.lock` to record the exact resolved dependency versions;
- Hatchling as the PEP 517 build backend;
- `pyproject.toml` as the single source of truth for Python project configuration.

The application package is located at:

```text
src/responsible_gaming/
```

Hatchling is explicitly configured to package this directory:

```toml
[tool.hatch.build.targets.wheel]
packages = ["src/responsible_gaming"]
```

## Consequences

### Positive

- Local development and CI use the same dependency resolution.
- Dependency changes automatically update both `pyproject.toml` and `uv.lock`.
- Development dependencies remain separate from runtime dependencies.
- The project follows modern Python packaging standards.
- A new contributor can reproduce the development environment with a single command:

```bash
uv sync
```

### Negative

- Contributors must install `uv`.
- The project depends on tooling that may be less familiar than `pip`.
- The team must avoid mixing `pip install` commands with `uv`.

## Rules

Production dependencies must be added using:

```bash
uv add <package>
```

Development dependencies must be added using:

```bash
uv add --dev <package>
```

Dependencies must be removed using:

```bash
uv remove <package>
```

Direct use of `pip install` is not part of the supported project workflow.

The following files must always be committed:

```text
pyproject.toml
uv.lock
```

Virtual environments must never be committed:

```text
.venv/
```

## Alternatives Considered

### pip, venv and requirements.txt

Rejected because dependency declaration, dependency locking and environment management would require multiple separate commands and files.

### Poetry

Not selected because the project does not require Poetry's broader project management workflow. `uv` provides all the dependency and environment management features required for this project while remaining lightweight.

### setuptools

Not selected as the build backend because Hatchling provides a simpler and more declarative configuration for a modern `pyproject.toml`-based project.
