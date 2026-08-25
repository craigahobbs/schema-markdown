# AGENTS.md

Guidance for AI assistants working in the schema-markdown dual-port projects.

This file is maintained in **both** repositories and should stay as identical as possible:

| Role | Repository |
|------|------------|
| Python | `schema-markdown` |
| JavaScript | `schema-markdown-js` |

When you change `AGENTS.md`, update **both** copies.

## Dual-port rule (mandatory)

The **Python** (`schema-markdown`) and **JavaScript** (`schema-markdown-js`) projects are **faithful ports of one another**. Treat them as one logical codebase expressed in two languages.

**Any change in one must be implemented in the other.** Never land a behavioral, structural, test, or API change on only one side.

### What “line-for-line identical” means

Keep the ports as **line-for-line identical as possible** for the **shared core**:

- Parser structure, control flow, branching order, and algorithm steps
- Type model (`TYPE_MODEL` / `typeModel`) Schema Markdown text and comments
- Validation control flow (type cases, attribute checks, error paths)
- Accepted **JSON-shaped** values (objects, arrays, strings, numbers, bools, null)
- Comments, error message text, and test cases (adapted only for language idioms)
- Module/file split and the relative structure of functions within a file
- Version numbers across releases when the shared surface changes

### Host-language carve-out (allowed differences)

Do **not** force parity for host surface that is not the shared core:

| Area | Examples |
|------|----------|
| Naming / packaging | `snake_case` vs `camelCase`; `pyproject.toml` vs `package.json`; `__init__.py` re-exports vs ESM named exports |
| Native validated types | Host objects accepted/returned as-is: Python `date` / `datetime` (returned), `Decimal` and `uuid.UUID` (accepted input); JS `Date` (returned), `Map` (accepted as dict/struct input). `uuid` **strings** are dual-port aligned — canonical `8-4-4-4-12` form, validated as strings on both ports |
| Native return types for date/datetime | Python `date` / `datetime` vs JS `Date`. Accepted ISO string inputs are dual-port aligned (a timezone is required, so the resulting instant matches); JS `Date` is millisecond-precision while Python keeps microseconds |
| Encode utilities | **By design** not dual-port identical: Python `JSONEncoder` + encoding args vs JS `jsonStringifySortKeys`; query-string helpers may differ in extras. Do not force encode API parity. |
| Tests / lint tooling | `unittest` vs `node:test`; pylint vs eslint; how `TEST=` selects cases |

Shared-core APIs map mechanically across languages (e.g. `ValidationError.member_fqn` ↔ `ValidationError.memberFqn`).

**Error message quoting (both value validation and type-model validation):** use **double quotes** for all quoted tokens on both ports. Value-validation **values** are compact JSON truncated to **100** characters; **type names** stay host-native (e.g. Python `str` / `NoneType` vs JS `string` / `object`). Multi-error lists must use the same sort order on both sides: type-model errors are sorted by `(typeName, memberName, message)` before joining, with a null/absent `memberName` ordered as an empty string. When one member is duplicated across multiple action sections, the offending section names are emitted in sorted order too.

Prefer structural parity over language-idiomatic rewrites **inside the shared core**. Do **not** refactor one port “while you’re here” without mirroring the other.

**Workflow:** when editing either port, open the paired file and apply the change in both before considering the work done. Run `make test` (and ideally `make commit`) in **both** repos.

Separate git repositories (not a monorepo): commits, PRs, and `make` run per-repo, but the **diff should still be a mirrored pair**. Language documentation lives in the JS repo: `static/language/` (path relative to `schema-markdown-js`).

## Project overview

**schema-markdown** defines and validates schemas with the [Schema Markdown language](https://craigahobbs.github.io/schema-markdown-js/language/). It parses Schema Markdown into a type model (plain dicts/objects), validates and type-massages values against that model, and provides small utilities (JSON encoding, query-string encode/decode).

| | Python (`schema-markdown`) | JavaScript (`schema-markdown-js`) |
|--|----------------------------|----------------------------------|
| Package | `schema_markdown` under `src/schema_markdown/` | npm `schema-markdown`, ESM (`"type": "module"`) |
| Library / tests | `src/schema_markdown/`, `src/tests/` | `lib/`, `test/` |
| Version / metadata | `pyproject.toml` | `package.json` |
| Docs | Sphinx + MyST under `doc/` | JSDoc; language docs in `static/language/` |
| License | MIT | MIT |

Downstream consumers include BareScript, Chisel, and other craigahobbs packages.

## Parallel modules

| Python | JavaScript | Role |
|--------|------------|------|
| `src/schema_markdown/parser.py` | `lib/parser.js` | Parse Schema Markdown → type model |
| `src/schema_markdown/schema.py` | `lib/schema.js` | Validate values / type model; helpers |
| `src/schema_markdown/type_model.py` | `lib/typeModel.js` | Meta-schema (`TYPE_MODEL` / `typeModel`) |
| `src/schema_markdown/schema_util.py` | `lib/schemaUtil.js` | Internal type-model error helpers |
| `src/schema_markdown/encode.py` | `lib/encode.js` | Encode / query-string helpers (host carve-out OK) |
| `src/schema_markdown/__init__.py` | (import from `lib/*.js`) | Python public re-exports |
| `src/tests/test_parser.py` | `test/testParser.js` | Parser tests (keep in lockstep) |
| `src/tests/test_schema.py` | `test/testSchema.js` | Schema/validation tests |
| `src/tests/test_encode.py` | `test/testEncode.js` | Encode/query-string tests |

Naming: Python `parse_schema_markdown`, `validate_type`; JS `parseSchemaMarkdown`, `validateType`. Map identifiers mechanically; do not rename or reorder **shared-core** logic on only one side.

## Build system

**Always drive work through `make`** in the repo you are changing. Read the matching skill before running tests, lint, coverage, or changing that Makefile:

| Repo | Skill |
|------|-------|
| `schema-markdown` | [python-build](https://github.com/craigahobbs/python-build#readme): [`../python-build/SKILL.md`](../python-build/SKILL.md) if that file exists, otherwise [https://raw.githubusercontent.com/craigahobbs/python-build/main/SKILL.md](https://raw.githubusercontent.com/craigahobbs/python-build/main/SKILL.md) |
| `schema-markdown-js` | [javascript-build](https://github.com/craigahobbs/javascript-build#readme): [`../javascript-build/SKILL.md`](../javascript-build/SKILL.md) if that file exists, otherwise [https://raw.githubusercontent.com/craigahobbs/javascript-build/main/SKILL.md](https://raw.githubusercontent.com/craigahobbs/javascript-build/main/SKILL.md) |

Local Makefile overrides:

- **Python:** `SPHINX_DOC := doc` (Sphinx + MyST under `doc/`)
- **JS:** `doc` also copies `static/*` into `build/doc/`

`TEST=` shape differs by port (see the skills): Python unittest ids use the `tests.` prefix; JavaScript is a `node --test` name pattern.

### Dual-port constraints (not in the skills)

1. **No multi-repo orchestration in Make is by design.** Coordinating Python + JS (paired edits, both gates, both commits/PRs) is the **agent’s and human’s job**, not the build system’s.
2. Dual-port checklist: change **both** ports; `make test` in each while iterating; `make commit` in **both** repos before commit/PR. Never weaken coverage, skip lint/doc, or run publish/gh-pages/changelog as part of ordinary work.

## Architecture (shared)

Core flow (both languages):

1. Parse Schema Markdown → type model (map of user type name → user type).
2. `validate_type` / `validateType(types, typeName, value)` → massaged value, or validation error.
3. Meta-schema (`TYPE_MODEL` / `typeModel`) describes and checks the type model itself.

Built-in types: `any`, `bool`, `date`, `datetime`, `float`, `int`, `string`, `uuid` (`object` is deprecated in favor of `any`).

Ordinary **JSON-shaped** input is the cross-port contract. Host-native types and exotic string forms may differ (see Dual-port carve-out).

### Type model validity (by design)

- **`parse_schema_markdown` / `parseSchemaMarkdown`** always returns a **valid** type model, or throws. Callers of the parser do not need a separate model check for parse results.
- **`validate_type` / `validateType`** assumes the `types` map is already a valid type model (well-formed types, acyclic bases, allowed attributes, etc.). Feeding an invalid model is a **usage error**; the validator does not re-prove model soundness (e.g. no cycle guards while walking struct/enum bases).
- If a type model was built by hand or may be invalid, call **`validate_type_model` / `validateTypeModel`** (or rely on parse) **before** validating values with it.

Do not add redundant model-validation work inside the value validator “for safety” unless the user explicitly asks to change this contract.

## Conventions

Shared (both ports):

- Prefer structural parity over language-idiomatic rewrites in the **shared core**.
- New features, bug fixes, tests, and error-message tweaks ship as **paired changes**.
- Bump **both** versions together (`pyproject.toml` and `package.json`) for shared releases.
- No new runtime dependencies without a strong reason (same constraint on both sides).
- Language doc updates go in `schema-markdown-js/static/language/`. Match existing section style (plain `##` sections, `**name** - description` lists; no novel tables or subsection titles unless the surrounding doc already uses them). Describe the language as multi-runtime capable, not Python+JS only. Per-package READMEs may mention this implementation's native types. Keep README/API examples accurate.
- Keep these two `AGENTS.md` files identical when editing project rules.

### Python

- 4-space indent, max line length **140** (`pylintrc`).
- MIT license header + GitHub license URL, then module docstring.
- Export new public symbols from `__init__.py`. Sphinx-style docstrings on public APIs.
- `unittest` tests; **100% line and branch coverage**.
- Docs: Sphinx + MyST under `doc/`.

### JavaScript

- ESM throughout; use `.js` extensions in import paths.
- MIT license header; JSDoc module tags (`/** @module lib/... */`).
- ESLint + c8 via make; **100%** coverage gate via `make cover` / `make commit`.
- Language static docs under `static/language/`.

## Related links

- Language: https://craigahobbs.github.io/schema-markdown-js/language/
- Python API docs: https://craigahobbs.github.io/schema-markdown/
- JS API docs: https://craigahobbs.github.io/schema-markdown-js/
- Python source: https://github.com/craigahobbs/schema-markdown
- JS source: https://github.com/craigahobbs/schema-markdown-js
