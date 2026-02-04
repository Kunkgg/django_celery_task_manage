# AGENTS.md

> This file defines rules for AI coding agents working in this repository.  
> Goal: keep the system **simple, maintainable, and pragmatic** — avoid over-engineering.

---

## Dev environment tips

- 使用 `uv add` 添加依赖（不要直接修改 pyproject.toml）
- 使用 `docker-compose up` 启动依赖服务（db / redis 等）
- 使用 `uv run python` 运行 Python 代码
- Django 管理命令统一通过：
  - `uv run python manage.py <command>`

---

## Project philosophy (VERY IMPORTANT)

This is a **business system**, not a framework, not a demo of design patterns.

AI agents MUST prefer:

- ✅ Simple code over clever abstractions  
- ✅ Readability over flexibility  
- ✅ Direct solutions over “future-proof architecture”  
- ✅ Django conventions over custom frameworks  

AI agents MUST AVOID:

- ❌ Creating new architectural layers without strong reason  
- ❌ Introducing generic abstraction for “possible future reuse”  
- ❌ Splitting files just to make things “look layered”  
- ❌ Adding design patterns (Factory, Strategy, etc.) unless already required by real complexity  
- ❌ Rewriting working code only for “clean architecture purity”

---

## Architecture boundaries

The project follows a **pragmatic Django layered structure**, NOT strict Clean Architecture.

### Allowed layers

| Layer | Responsibility |
|------|----------------|
| **View (Django View / DRF ViewSet)** | HTTP handling, request parsing, response formatting |
| **Service layer** | Business logic, orchestration |
| **Model layer** | Data structure + simple domain behavior |
| **Repository logic (optional)** | Complex query logic only |

---

### ❗ Rules AI must follow

#### 1. Business logic MUST NOT live in View

Views should only:
- Validate input
- Call service functions
- Return response

If logic is more than **~10–15 lines**, move to service.

---

#### 2. DO NOT create “domain layer” unless project already has one

This project does **not** enforce DDD.

AI must NOT introduce:

- `domain/`
- `entities/`
- `aggregates/`
- `use_cases/`

Unless explicitly asked by a human.

---

#### 3. Service layer rules

Services are:

- Plain Python functions or simple classes
- No inheritance hierarchies
- No abstract base classes unless already present
- No dependency injection frameworks

Good:

```python
def create_order(user, items):
    ...
```

Bad:

```python
class BaseOrderService(AbstractOrderServiceFactory):
    ...
```

---

#### 4. Models are NOT just data containers

Allowed in models:

- Simple validation
- Small domain rules tightly coupled to the model
- Query helpers

Avoid:

- Huge business processes
- Cross-model workflows

---

#### 5. Database access

- Prefer Django ORM
- Raw SQL only when performance or complexity requires
- Do NOT wrap ORM in generic repository classes unless repeated complex queries appear

---

## Code style rules

AI agents must:

- Follow existing code style in the file
- Avoid introducing new coding paradigms in the same module
- Keep functions under ~40 lines where possible
- Avoid deep nesting (>3 levels)

---

## When adding new features

AI must ask internally:

1. Can this be done by extending an existing service?
2. Can this stay inside current app instead of creating a new app?
3. Is this abstraction solving a real current problem?

If answer is “no”, do the simpler thing.

---

## What AI should NOT do automatically

- ❌ Split one service into multiple layers “for clarity”
- ❌ Introduce DTO objects everywhere
- ❌ Add mappers between identical structures
- ❌ Add configuration systems for fixed logic
- ❌ Add plugin systems

---

## Testing expectations

- Prefer testing service layer
- Avoid heavy mocking of Django internals
- Use real models when possible

---

## Summary for AI agents

> This project values **practical engineering over textbook architecture**.

If unsure, choose the solution that:

**Has fewer files, fewer abstractions, and is easier for a mid-level Django developer to understand in 6 months.**
