# agents_poc

A small, extensible proof of concept for **rule-based conversational agents**: agents that, on every turn, answer the user, extract structured data from the conversation, and — based on business rules — trigger an external action through a (simulated) HTTP integration.

Two agents are implemented on top of the same shared architecture:

- **`DebtAgent`** — registers a payment commitment for a pending debt (`POST /v1/commitment`) once both a commitment date and a committed amount have been captured.
- **`AssistanceAgent`** — registers a customer support request (`POST /v1/request`) once the user's request has been captured.

No LLM and no real HTTP calls are involved — both are simulated, as described in [Architecture](#architecture).

---

## Getting started

### Prerequisites

- Python **3.13** (see [.python-version](.python-version))
- [uv](https://docs.astral.sh/uv/) as the package/dependency manager (the project has no `requirements.txt`; everything is declared in [pyproject.toml](pyproject.toml) / [uv.lock](uv.lock))

### Install dependencies

```bash
uv sync
```

This creates a local `.venv` and installs both runtime dependencies (`httpx`, `pydantic`, `pydantic-settings`) and dev dependencies (`pytest`, `ruff`).

> `pyproject.toml` + [`uv.lock`](uv.lock) are the actual source of truth for dependencies — a `requirements.txt` is **not** needed with `uv`. A [`requirements.txt`](requirements.txt) is still committed here, generated from the lockfile (`uv export --format requirements.txt --no-hashes -o requirements.txt`), purely as a fallback for environments without `uv` (`pip install -r requirements.txt`). Regenerate it after changing dependencies rather than editing it by hand.

### Configuration (secrets)

Runtime configuration (API token, endpoint URLs) is loaded from `secrets/.env.<environment>` via [`src/config/settings.py`](src/config/settings.py), selected through the `APP_ENV` environment variable (`dev` by default). The expected variables are:

```
API_TOKEN=
COMMITMENT_API_ENDPOINT=
REQUESTS_API_ENDPOINT=
```

`secrets/.env.dev`, `secrets/.env.staging` and `secrets/.env.prod` already exist locally — fill in real values there. `secrets/.env.*` is git-ignored, so these files are never committed.

### Run the demo

```bash
uv run agents-poc
```

This runs [`src/main.py`](src/main.py), which wires up one `DebtAgent` and one `AssistanceAgent` with simulated conversation/parser models and a shared `SimulatedHttpClient`, and executes one `handle_turn()` per agent — printing the user-facing response and the details of the simulated HTTP call each action triggers.

Equivalent alternative: `uv run python -m src.main`.

### Run the tests

```bash
uv run pytest -q
```

### Lint

```bash
uv run ruff check .
```

---

## Architecture

### The turn lifecycle

Every agent is a subclass of [`BaseConversationalAgent`](src/agents/base_conversational_agent.py) and exposes a single public method, **`handle_turn()`**, which is the whole contract of "one turn of conversation":

```
handle_turn()
 ├─ 1. response = conversation_model.answer_user()      → what the user sees
 ├─ 2. raw_data = parser_model.parse_data()              → structured info extracted from the conversation
 ├─ 3. action   = self._build_action(raw_data)            → validate + normalize + decide (agent-specific)
 └─ 4. if action and not already sent this conversation:
          action.execute(http_client)                     → fire the external integration
    return response
```

```
 ConversationModel        ParserModel
        │                       │
        ▼                       ▼
  answer_user()          parse_data()
        │                       │
        │                       ▼
        │              _build_action(raw_data)   ← agent-specific validation/normalization
        │                       │
        │              BaseAction | None
        │                       │
        │           (skip if None, or if payload already sent)
        │                       │
        │                       ▼
        │                 action.execute(http_client)
        │                       │
        ▼                       ▼
     response            SimulatedHttpClient.post(...)
```

Steps 1–2 are delegated to two collaborator objects the agent receives by dependency injection — it never knows *how* the answer is produced or *how* the conversation is parsed, only that both objects fulfill a `Protocol`:

- **`ConversationModel`** ([`src/protocols/conversations.py`](src/protocols/conversations.py)): `answer_user() -> str`. In production this would wrap an LLM call; here it's simulated by [`SimulatedConversationModel`](src/simulation/simulated_conversation_model.py).
- **`ParserModel`** ([`src/protocols/parsers.py`](src/protocols/parsers.py)): `parse_data() -> dict[str, str]`. In production this would be another LLM/NLU call that extracts structured fields from the conversation history; here it's simulated with hardcoded dicts (e.g. [`SimulatedDebtParserModel`](src/simulation/simulated_debt_parser_model.py)).

Because both are `Protocol`s (structural typing), **no inheritance is required** to plug in a new implementation — any object exposing the right method works.

### Validation, normalization and the "should I act?" decision

Step 3, `_build_action(raw_data)`, is the one abstract method every agent must implement — it's where all agent-specific business logic lives:

- **`DebtAgent`** ([`src/agents/debt_agent.py`](src/agents/debt_agent.py)) validates `raw_data` against the [`CommitmentData`](src/schemas/commitment.py) pydantic schema (`commitment_date: str | None`, `committed_amount: float | None`). If validation fails, or either field is still `None`, no action is built. Otherwise it returns a `DebtCommitmentAction` with the normalized payload.
- **`AssistanceAgent`** ([`src/agents/assistance_agent.py`](src/agents/assistance_agent.py)) does the same against [`RequestData`](src/schemas/request.py) (`request: str | None`).

Pydantic schemas are used here for two reasons: they give free type coercion/validation (`ValidationError` on malformed data → treated as "not ready yet, don't act"), and they're the natural place to add new required/optional fields as a use case grows.

### Actions and the HTTP integration

An **action** ([`src/actions/base_action.py`](src/actions/base_action.py)) represents "the external side effect this turn should trigger". `BaseAction` is abstract and holds the payload plus the shared header-building logic:

```python
class BaseAction(ABC):
    payload: dict[str, str]

    def _build_headers(self, parsed_data): ...   # Bearer auth + parsed fields as headers
    @abstractmethod
    def execute(self, http_client: HttpClient) -> None: ...
```

- **Authentication**: every request carries `Authorization: Bearer {secrets.API_TOKEN}` — built once in `BaseAction._build_headers`, so no concrete action re-implements auth.
- **Extra headers**: all non-`None` fields returned by the `ParserModel` are also sent as headers (as required by the exercise spec), stringified.
- Concrete actions ([`DebtCommitmentAction`](src/actions/debt_commitment_action.py), [`AssistanceRequestAction`](src/actions/assistance_request_action.py)) only decide **where** to POST — the endpoint URL (read from `secrets`) — and pass the payload through as both headers and body.

The HTTP call itself goes through the **`HttpClient`** protocol ([`src/protocols/http_client.py`](src/protocols/http_client.py)): `post(url, headers, body) -> httpx.Response`. The only implementation, [`SimulatedHttpClient`](src/integrations/http.py), builds a **real** `httpx.Request` (so URL/header/body validation and serialization genuinely happen — a malformed URL or a non-ASCII header value will raise, just like with a real client) but never sends it over the network; it logs the request and always returns a synthetic `200 OK`.

### Deduplication

`BaseConversationalAgent` keeps a private `set[frozenset]` (`self._sent_payloads`) scoped to the agent instance (i.e. to one conversation). Before executing an action it computes `frozenset(action.payload.items())` and checks whether that exact payload was already sent; if so, it skips `execute()` this turn. This guarantees the same commitment/request is never registered twice in a row while the conversation keeps producing the same structured data, while still allowing a genuinely new payload (e.g. the user changes the amount) to go through.

### Configuration

[`src/config/settings.py`](src/config/settings.py) exposes a single `secrets` singleton (a `pydantic-settings` `BaseSettings`), loaded from `secrets/.env.<APP_ENV>` (defaults to `dev`). Actions read `secrets.API_TOKEN`, `secrets.COMMITMENT_API_ENDPOINT`, `secrets.REQUESTS_API_ENDPOINT` from it. Because it's a plain mutable object, tests override it with `monkeypatch` instead of depending on real `.env` values (see [`tests/conftest.py`](tests/conftest.py)).

---

## Project structure

```
src/
├── main.py                 # Demo entrypoint: wires everything and runs one turn per agent
├── config/                 # Environment-based settings (secrets singleton)
├── protocols/               # Structural interfaces (Protocol): ConversationModel, ParserModel, HttpClient
├── schemas/                 # Pydantic models used to validate/normalize parsed data per use case
├── agents/                  # BaseConversationalAgent + one subclass per use case
├── actions/                  # BaseAction (auth/headers) + one subclass per external side effect
├── integrations/             # Concrete HttpClient implementation(s)
└── simulation/                # Fakes for ConversationModel/ParserModel used by the demo (no real LLM)

tests/                        # Mirrors the src/ layout; see "Run the tests" above
```

| Folder | Contains | Extend by |
|---|---|---|
| `agents/` | One class per use case, each owning the "what data do I need, and when should I act" decision. | Adding a new `BaseConversationalAgent` subclass. |
| `actions/` | One class per external side effect the system can trigger. | Adding a new `BaseAction` subclass. |
| `schemas/` | One pydantic model per use case's structured data shape. | Adding a new `BaseModel` with the fields that use case needs. |
| `protocols/` | The three structural interfaces every collaborator must satisfy. | Only touched when introducing a genuinely new kind of collaborator (e.g. a second `HttpClient`-like method). |
| `integrations/` | Real/simulated implementations of `HttpClient`. | Adding a new class implementing `HttpClient.post(...)` (e.g. a real `httpx`-backed one). |
| `simulation/` | Fakes standing in for the LLM-backed `ConversationModel`/`ParserModel`, used only by `main.py`'s demo. | Adding a new fake per new agent, or swapping these for real LLM-backed implementations later. |

---

## How to extend

### Add a new agent (new use case)

1. **Define the data shape** it needs, in `src/schemas/<use_case>.py`, as a pydantic `BaseModel` with the fields the parser is expected to return (mark fields `| None = None` for "not captured yet").
2. **Define the action** it triggers, in `src/actions/<use_case>_action.py`, subclassing `BaseAction`:
   ```python
   class MyAction(BaseAction):
       def execute(self, http_client: HttpClient) -> None:
           http_client.post(
               url=secrets.MY_ENDPOINT,
               headers=self._build_headers(self.payload),
               body=self.payload,
           )
   ```
   Add the corresponding endpoint variable to `secrets/.env.*` and `src/config/settings.py` picks it up automatically (`extra="allow"`).
3. **Define the agent**, in `src/agents/<use_case>_agent.py`, subclassing `BaseConversationalAgent` and implementing the one abstract method:
   ```python
   class MyAgent(BaseConversationalAgent):
       def _build_action(self, raw_data: dict[str, str]) -> BaseAction | None:
           try:
               data = MySchema.model_validate(raw_data)
           except ValidationError:
               return None
           if <fields not ready yet>:
               return None
           return MyAction(data.model_dump(mode="json", exclude_none=True))
   ```
   Everything else — fetching the response, calling the parser, deduplication — is inherited for free from `BaseConversationalAgent`.
4. **Wire it up**: instantiate `MyAgent(conversation_model, parser_model, http_client)` wherever it's needed (in `src/main.py` for the demo, or in whatever drives real conversations in the future) and call `.handle_turn()`.
5. **Test it** following the existing pattern in `tests/agents/`: unit-test `_build_action` directly (valid data → action; missing/invalid data → `None`), and reuse `tests/conftest.py`'s `FakeConversationModel`/`FakeParserModel`/`RecordingHttpClient` for a `handle_turn()`-level test.

### Add a new action to an existing agent

Add the `BaseAction` subclass as above, then extend that agent's `_build_action` to return it (or a different action) based on whatever new condition applies — `_build_action` can inspect more fields than the ones triggering the current action.

### Swap the HTTP integration (e.g. call the real APIs)

Implement `HttpClient` ([`src/protocols/http_client.py`](src/protocols/http_client.py)) with a class that actually sends the request (e.g. `httpx.Client().post(...)` instead of only constructing it), and inject that instance instead of `SimulatedHttpClient` wherever agents are built. Nothing in `agents/` or `actions/` needs to change — they only depend on the `HttpClient` protocol.

### Swap the conversation/parser models (e.g. plug in a real LLM)

Implement `ConversationModel` / `ParserModel` with classes backed by a real LLM call (LangChain, LlamaIndex, a direct SDK call, etc.) instead of the hardcoded `src/simulation/` fakes, and inject them into the agent constructor. Again, no change is required in `agents/`, `actions/`, or the deduplication logic, since agents only depend on the protocol's method signature.

---

## What's deliberately out of scope (PoC vs. production)

This repository is a proof of concept for the agent/action architecture, not a production service. A few things are intentionally missing or simplified, and would need to be addressed before this could run in production:

- **`ConversationModel` and `ParserModel` are not production implementations.** `src/simulation/` exists only to exercise this project's turn lifecycle without a real LLM. In production, `answer_user()` would call an actual model (an LLM provider SDK, LangChain, LlamaIndex, …) and `parse_data()` would run real extraction/NLU over the conversation. Both would also need real conversation *state*: [`ConversationState`](src/simulation/conversation_state.py) currently just holds `chat_id`/`history`/`last_user_message` in memory and is thrown away when the process exits — a real implementation would persist conversation history and any extracted-so-far fields in an actual database (e.g. Postgres, or a document store), not in a Python attribute.
- **Deduplication is in-memory and per-process.** `BaseConversationalAgent._sent_payloads` lives only inside one agent instance's memory, for the lifetime of that process. It works for this PoC (one process, one conversation, one turn at a time) but would not survive a restart, would not be shared across multiple app instances behind a load balancer, and offers no way to inspect "what was already sent" from the outside. In production this state (and the conversation state above) would live in a shared store such as **Redis** or a database table, keyed by conversation/chat id.
- **No server, no containerization.** There is currently no HTTP server exposing these agents (`main.py` is a local script demo), and no `Dockerfile`/`docker-compose` to run this as a deployable service. That's a deliberate simplification for the exercise, not a limitation of the architecture: because agents only depend on the `ConversationModel`/`ParserModel`/`HttpClient` protocols, wrapping `handle_turn()` behind an HTTP endpoint is a thin addition — a lightweight ASGI framework like **[Litestar](https://litestar.dev/)** (already a natural fit given `pydantic` is already a dependency) would let a `POST /conversations/{id}/turn` endpoint be added quickly, with the actual agent wiring unchanged, and then containerized with a standard `Dockerfile`.

---

## Logging

Logging is configured once, centrally, via [`configure_logging()`](src/config/logging_config.py), called at the top of `main()` in [`src/main.py`](src/main.py). It sets the root logger's level based on `secrets.environment` (`APP_ENV`): `DEBUG` in `dev`, `INFO` in `staging`/`prod`.

To log from any module, get a module-scoped logger the standard way:

```python
import logging

logger = logging.getLogger(__name__)

logger.info("Something happened: %s", details)
logger.exception("Call to %s failed", url)  # inside an `except` block — includes the traceback
```

- Use `logger.exception(...)` (not `logger.error(...)`) inside an `except` block to capture the traceback automatically — see [`AssistanceRequestAction.execute`](src/actions/assistance_request_action.py) and [`DebtCommitmentAction.execute`](src/actions/debt_commitment_action.py) for the pattern.
- [`SimulatedHttpClient`](src/integrations/http.py) logs the simulated request at `INFO` (method/URL) and `DEBUG` (headers/body).
- Never call `configure_logging()` more than once per process, and never call it from a library module — only from an entrypoint (`main.py`, or a future server entrypoint).