# TODO - Account Lockout Protection (Agri-Vision)

## Phase 1: Discovery & Architecture
- [x] Read `app.py` login flow
- [x] Read `models.py` User model
- [x] Read `services/lockout_service.py` (existing skeleton)
- [x] Read `services/rate_limit_store.py` (memory/redis)
- [x] Read `config/rate_limit_config.py` (existing lockout envs)
- [x] Read `auth/audit_log.py`
- [ ] Produce full internal architecture + integration mapping

## Phase 2: Implementation
- [ ] Extend `services/lockout_service.py` to expose lock transition result and cooldown info
- [ ] Add lockout policy config/env validation (reuse `config/rate_limit_config.py` or extend)
- [ ] Update `models.py` User model with lockout fields (failed attempts, timestamps, locked until, IPs)
- [ ] Update `app.py` `/login` route:
  - [ ] check lockout status before password verification
  - [ ] record failed attempts on wrong password
  - [ ] reset counters + unlock fields on successful login
  - [ ] add security audit events for auth success/fail/locked/unlocked
  - [ ] keep response/message consistent (no user enumeration)
- [ ] Add migration strategy/tooling (or ensure `db.create_all()` covers new fields in tests)

## Phase 3: Testing
- [ ] Unit tests for `services/lockout_service.py`
- [ ] Unit tests for lockout policy/env validation
- [ ] Integration tests for Flask `/login` lockout behavior
- [ ] Security tests for response consistency / no enumeration
- [ ] Regression: ensure existing tests still pass

## Phase 4: Build/CI/Vercel
- [ ] Run `pytest`
- [ ] Run lint/type-check/build (repo scripts)
- [ ] Ensure CI (GitHub Actions) passes
- [ ] Ensure Vercel deployment is safe (no server-only imports at module scope)

## Phase 5: Documentation & Changelog
- [ ] Update README/security docs + env var guide
- [ ] Add CHANGELOG entry for lockout feature

