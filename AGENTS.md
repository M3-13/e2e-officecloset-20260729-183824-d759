<!-- office-crew-developer-conventions: v15 -->
<!-- office-crew-developer-md: full -->
# Workspace conventions for AI developers

You are a developer in a team working on a single ticket. Read `SPEC.md` for
the full sprint scope, then implement YOUR ticket.

## Hard rules

0. **Act, don't announce.** Never end a turn with only a sentence like
   "Let me read SPEC.md" or "I'll create the file" and then stop. If you say you
   will do something, your VERY NEXT step MUST be the actual tool call
   (Read/Write/Edit/Bash) — in the same turn. A turn that contains only prose
   and no tool call counts as zero work done and wastes a round.

1. **Do NOT overwrite existing files from scratch.** Always Read first, then
   add to / modify them. This is especially important for `app/main.py`,
   `requirements.txt`, `pyproject.toml`, `README.md` — other tickets may have
   added content there that you must preserve.

2. **Module naming is fixed.** Use the names that already exist in the repo.
   If you see `app/db.py`, do not create `app/database.py`. If unsure, grep
   for usages first.

3. **Never commit generated files.** The `.gitignore` already excludes
   `__pycache__/`, `*.pyc`, `*.db`, `.venv/`. Don't `git add -A` if you have
   such files in the working tree — use explicit paths.

4. **Tests are part of done.** Every ticket includes writing tests AND making
   them pass. `cd backend && PYTHONPATH=. python -m pytest` must exit 0 before you stop.

   **A green run here does NOT mean a green pipeline.** This machine is a
   developer workstation with many packages already installed; the CI starts from
   an empty container and installs ONLY what the manifest declares. So a
   dependency you use but forget to declare imports fine here and dies there at
   collection time — the whole suite, not one test. Before you finish: for every
   third-party module your code imports, check that it (or the extra that brings
   it) is in `requirements.txt` / `pyproject.toml`. Watch the ones that arrive as
   an EXTRA rather than a package of their own — `pydantic.EmailStr` needs
   `pydantic[email]`, `python-jose[cryptography]`, `uvicorn[standard]`,
   `passlib[bcrypt]`. Adding a dependency is part of the change that uses it.

5. **Stay within your ticket.** No drive-by refactors of unrelated code, even
   if it looks improvable. Note observations in the commit message instead.

6. **Do NOT create branches or push.** The orchestrator handles all git
   operations after you. Just commit-worthy state in the working tree is
   enough — actually, don't even commit; the orchestrator does that too.

6b. **Never run a command that does not return on its own.** A dev server,
   a watcher or a REPL keeps running until it is killed, so the shell call
   never comes back — you sit there producing no output and the run is
   eventually cut off, mid-ticket, with the last step unfinished. This is the
   single most common way a ticket is lost.

   **Do NOT start a server to check your endpoints — not even a "bounded" one
   you intend to kill afterwards.** Assert them IN-PROCESS instead:

   ```python
   from fastapi.testclient import TestClient
   def test_register_and_login():
       c = TestClient(app)
       assert c.post("/auth/register", json={...}).status_code == 201
       assert c.post("/auth/login", json={...}).status_code == 200
   ```

   This is not a style preference — the background-and-kill recipe cannot be
   made to work here, and it cost real tickets before this rule existed. The
   shell captures `$!`, but on Windows `py`/`python` is launched through a
   store alias that starts the REAL interpreter as a separate process, so the
   pid you saved belongs to a launcher that has already exited. Your `kill`
   then hits nothing: the server keeps the port AND keeps the pipe your own
   command writes to open, so the tool call never returns and your run is cut
   off with the last step unfinished — with every file you wrote still there
   and no way to say you were done.

   `TestClient` needs no port, no pid and no cleanup, exercises the same
   routes, and its result is a test that stays in the repo. Tessa runs the
   real server later; proving the process boots is HER job, not yours.

   Same rule for the frontend: `npm run build` tells you it compiles;
   `npm run dev` never finishes. And if a port is already taken, do NOT wait
   or retry in a loop — that is a second way to never return.

7. **Ask questions when stuck — DON'T guess.** If the ticket or SPEC is
   ambiguous on a decision that affects the result (e.g. "should pagination
   default to 20 or 50?", "sync or async client?", "what behavior on duplicate
   input?"), do this instead of inventing an answer:

   The same applies when a requirement is NOT ambiguous but you believe it is
   WRONG — a wrong HTTP verb, a contradiction inside the ticket, a name that
   fights the convention the rest of the code follows. That case has no obvious
   home: rule 1 says implement exactly the ticket, and your judgement says the
   ticket is mistaken. **What you must NOT do is quietly build the better
   version.** The reviewer judges the diff against the ticket, so a silent
   deviation is the one outcome that is guaranteed to block the merge — and
   nobody learns the ticket was wrong. So: implement it AS WRITTEN, and end your
   final message with one line per objection, in exactly this form:

   ```
   OBJECTION: <which requirement, and why you believe it is wrong>
   ```

   That line is read mechanically — it reaches the reviewer, the merge request
   and the Tech Lead, so the NEXT ticket can be better. Prose without the marker
   reaches no one. If following the requirement would produce something
   contradictory or actively harmful, use `QUESTION.md` and stop instead.

   - Write a file `QUESTION.md` in the repo root with:
     ```
     # Question to Tech Lead

     **Context**: <which file / which spec point is unclear>

     **Question**: <your specific question, with options if any>

     **Why it matters**: <how the choice changes the implementation>
     ```
   - Then STOP working. Do NOT write code that depends on the unknown choice.
     Do NOT commit anything. Exit cleanly.
   - The Tech Lead (or the architect) will answer in `ANSWER.md`, then you'll
     be re-spawned to continue. You'll find `ANSWER.md` in the repo root.
   - When you read `ANSWER.md`: act on the answer immediately, then DELETE
     `QUESTION.md` and `ANSWER.md` (no clutter in the MR).

   Limit: max 3 questions per ticket. Use this for real decisions, not for
   trivial style choices — for those, make a reasonable choice and document it
   in a code comment as before.

<!-- office-crew-developer-subagents: verifier -->
## Subagents: pre-push self-review (MANDATORY)

Before you consider your work done: delegate ONE task-tool call to the
`pre-push-reviewer` subagent — hand it a one-line ticket summary and ask it to
check the current worktree state against the ticket and to run the lint/test
commands from this file. Skip the delegation ONLY for a trivially small change
(a one-line fix).

Its findings are EVIDENCE, and you must resolve each one explicitly:

- Fix it, or state in your final message why it is a false positive. Those are the
  only two endings. Silently keeping your original version is neither.
- If you disagree, RE-RUN the command it ran and quote the real output. The
  reviewer executes the pipeline's own commands; a finding you cannot reproduce is
  worth reporting, one you simply dislike is not.
- Never revert a change to undo a finding. On 2026-07-28 a developer took the
  reviewer's correct import fix back out, and the pipeline went red twice on
  exactly the defect the reviewer had named — the round trip cost more than the
  whole ticket.
- The reviewer cannot write. If it says a file needs changing, YOU change it.

## CI/CD is active (GitHub Actions with Quality Pack)

The repo has a `.github/workflows/ci.yml`. On every `git push` the following runs automatically:
- **test** (pytest; coverage is measured and printed) — BLOCKING on test FAILURES
- **lint** (`ruff format --check` + `ruff check`) — BLOCKING
- **types** (mypy with `--ignore-missing-imports`) — warning, not blocking
- **security** (pip-audit + bandit) — warning, not blocking

Important consequences for you:
1. **`pytest` must be green locally.** A failing or non-collecting test kills the CI.
   Write tests for the behaviour YOUR ticket adds. There is NO coverage threshold —
   do not write tests against stubs or scaffolding just to raise a percentage; the
   ticket that implements them brings their tests with it.
2. **Run `ruff format .` locally** before you finish. CI checks that
   everything is formatted.
3. **`ruff check .` must be green** — fix all violations. See `ruff.toml` in the
   repo root for the configuration.
4. **Type hints are expected** (even though the types stage is not blocking):
   every public function needs argument types + a return type.
5. **No hardcoded secrets/keys/URLs** — bandit catches that. Use env vars.
6. **`requirements.txt` must be up to date.** New libs → add them.

## Documentation requirement

The repo MUST ship with a REAL `README.md` at the root — never just the repo
name or the GitHub auto-init stub. It MUST contain:
- a one-paragraph project description;
- the tech stack;
- install steps;
- how to RUN in dev AND (if there is a build) how to BUILD for production;
- HOW TO USE IT — describe whatever actually fits THIS product: controls/key
  bindings for a game, the main screens and actions for an app, the public
  API (endpoints/functions) for a service or library, the commands and flags
  for a CLI. Not every project has "controls" — document what this one has;
- the feature list.
Keep it in sync with your ticket — new endpoints / functions / config / controls
get reflected here. For REST APIs also give, per endpoint: method, body schema,
response example. For a CLI, show example invocations; for a library, a minimal
usage snippet. If the project has a `docs/` structure, deep docs go there but
the README stays the entry point.

The reviewer REJECTS an MR whose product ships without this README.

## RUN.json — how this product starts (BINDING, and it is EXECUTED)

The repo root carries `RUN.json`: the machine-readable half of the README's
"how to run". Tessa's test runner and the CI pipeline do not guess how to start
this product — they read this file and execute exactly what it says. A start
command that does not start the product is a defect of the same severity as a
crash, and prose in the README that disagrees with this file is a defect too.

One entry per startable part:

```json
{
  "runcontract": 1,
  "services": [
    {
      "name": "api", "dir": "backend", "stack": "python", "kind": "server",
      "install": [["${python}", "-m", "pip", "install", "-q", "-r", "requirements.txt"]],
      "start": ["${python}", "-m", "uvicorn", "app.main:app", "--port", "${PORT}"],
      "port": 8000, "port_env": "PORT",
      "health": { "path": "/api/health", "expect_status": [200] },
      "env": {
        "DATABASE_URL": { "dev": "sqlite:///./dev.db" },
        "JWT_SECRET":   { "generate": "hex", "bytes": 32 },
        "STRIPE_KEY":   { "external": true,
                          "degraded_without": "POST /api/checkout answers 503" }
      }
    }
  ]
}
```

- Commands are **argv lists**, never shell strings (`["npm", "run", "build"]`).
- Placeholders, and only these three: `${python}` (the interpreter running the
  service), `${PORT}` (the port actually bound), `${service:<name>.origin}` (the
  URL another declared service ended up on — use it for CORS origins and for a
  frontend's API base, and never hardcode a port instead).
- Every variable the process needs to BOOT belongs here, in exactly one class:
  `dev` (a literal that is demonstrably not a secret), `generate` (a recipe —
  the value is rolled per run and never exists in the repo), or `external` (no
  value at all: the product MUST boot without it and degrade, and
  `degraded_without` says what stops working).
- **A secret never has a value here.** `JWT_SECRET: {"dev": "..."}` is rejected —
  that is a signing key in a git repository. Use `generate` or `external`.
- Config is read LAZILY, never at import time. `os.environ["X"]` in a module
  body or a class body kills the process before it can serve anything, and no
  default and no error message can help the person who cloned the repo.
- `kind`: `server` (needs `health` or `ready_log`), `static` (needs
  `serve_dir` — the built output), `cli`, `worker`.
- Keep it TRUE as the product grows: a ticket that adds a variable, a port, an
  endpoint used as health check or a whole service updates this file in the same
  MR. If you cannot state a field honestly, leave it out rather than guess.
- You do NOT need to start a server to write this (rule 7 still forbids that) —
  you DECLARE how it starts, Tessa PROVES it.

## Design tokens (UI projects only — when DESIGN.md is in the repo)

If the file `DESIGN.md` exists in the repo root, **IT IS BINDING** for all
visual decisions:

1. **Do not improvise your own hex colors.** When you need a color, use exactly
   one from the `## Colors` section of DESIGN.md. Ideally as a CSS
   custom property: `:root { --color-bg: #...; }` (from the tokens), then in the
   code just use `var(--color-bg)`.
2. **Spacing comes from the scale.** No random `padding: 13px` — if the
   scale has 4/8/12/16/24, take a value from it. Also think in custom properties:
   `--space-0`, `--space-1`, etc.
3. **Border radii from DESIGN.md** — do not guess them yourself.
4. **Follow the component specs.** If DESIGN.md says "Button: padding 12/24,
   radius md, min-height 44px" — implement it exactly that way, not "approximately".
5. **If DESIGN.md does not specify a component** that your ticket needs:
   improvise GENTLY in the same style (same tokens, same logic
   as the other components). Note it in the commit message: "new component X
   improvised without a spec — the designer can align it later".
6. **Never touch DESIGN.md** — it is maintained by the designer (Luna).

The reviewer checks token consistency on UI MRs.

## UI/UX Pro Max Skill (use on UI/frontend tickets)

On this system the Claude Code skill **`ui-ux-pro-max`** is installed globally
(67 styles, 96 palettes, font pairings, UX guidelines, stack best practices).
If your ticket builds visible UI (pages, components, styling, landing,
dashboard), use it BEFORE and DURING the implementation:

1. **Pull the design system** (pattern, style, colors, typography, effects,
   anti-patterns for the project type):
   ```
   py "C:/Users/Anwender/.claude/skills/ui-ux-pro-max/scripts/search.py" "<product type industry keywords>" --design-system -f markdown
   ```
2. **Get the stack guidelines** (default stack `html-tailwind`):
   ```
   py "C:/Users/Anwender/.claude/skills/ui-ux-pro-max/scripts/search.py" "<topic>" --stack html-tailwind
   ```
3. **Invocation rule (IMPORTANT):** always use `py` + the ABSOLUTE path exactly as above.
   `python` / `python3` are broken Store stubs on this system and will
   fail.
4. **Priority on UI projects:** if a `DESIGN.md` is in the repo, its tokens
   ALWAYS win (colors/spacing/radii — maintained by Luna). The skill
   only fills in where DESIGN.md is silent: UX patterns, accessibility,
   hover/transitions, stack idioms and the pre-delivery checks.

## Project layout (fullstack)

This is a fullstack project. **All Python backend code, tests AND
`requirements.txt` live in `backend/`** (`backend/app.py`, `backend/tests/`,
`backend/requirements.txt`). **All frontend files live in `frontend/`.** Put
nothing Python at the repo root — the CI runs the backend test suite from inside
`backend/` and the frontend checks from inside `frontend/`.

## Quick context

- Stack: depends on project — read existing files first to find out
- For Python/FastAPI projects: DB usually in `app/db.py`, tests via pytest
- For frontend projects: see "Browser frontends" section below

## Browser frontends (HTML/CSS/JS for direct browser use)

If your ticket produces files that are meant to be opened in a browser:

1. **The README MUST contain a "How to run" section**, because `file://` URLs
   break ES-Modules, fetch(), and most modern web APIs (CORS blocks them).
2. Minimum acceptable instructions:
   - Static files only: `py -m http.server 8000`, then open `http://localhost:8000`
   - Or: use VS Code Live Server extension
   - If a build tool is involved (Vite, Webpack, etc.): the exact build + serve commands
3. If you write a small launcher script (e.g. `start.bat` on Windows, `start.sh` on Unix), even better.
4. Do NOT assume the user knows to start an HTTP server. State it explicitly.

This applies regardless of whether tests are required for the ticket.

## Separate Frontend + Backend (cross-origin) — CORS is mandatory

If your ticket creates a Frontend that talks to a separate Backend (Vite + FastAPI,
React + Flask, etc.), CORS MUST be configured from the start:

- **FastAPI:** add `CORSMiddleware` for the dev-server origins:
  ```python
  from fastapi.middleware.cors import CORSMiddleware

  app.add_middleware(
      CORSMiddleware,
      allow_origins=[
          "http://localhost:5173",   # Vite default
          "http://localhost:5174",   # Vite fallback
          "http://localhost:3000",   # CRA / Next.js
      ],
      allow_credentials=True,
      allow_methods=["*"],
      allow_headers=["*"],
  )
  ```
- **Flask:** `from flask_cors import CORS; CORS(app, origins=[...])`
- The default behavior without CORS is: the browser blocks — the user sees
  `Access-Control-Allow-Origin` missing errors, the app is unusable.

If you don't know the exact frontend port: include common dev-server ports as above.
If a user-given config indicates production, use the proper production origin instead.
