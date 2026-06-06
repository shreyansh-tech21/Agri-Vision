# TODO - Device-Based Session Management (Agri-Vision)

## Phase 1 - Repository Discovery
- [x] Identify existing auth: Flask-Login and JWT refresh rotation modules.
- [x] Confirm JWT rotation uses refresh token families with replay detection.
- [ ] Confirm/locate existing JWT HTTP endpoints (none found in app.py).

## Phase 2 - Session Management Implementation
- [ ] Add `DeviceSession` model + indexes in `models.py`.
- [ ] Add UA/OS/browser/device detection module.
- [ ] Add `services/session_service.py` with create/list/touch/revoke.
- [ ] Add JWT middleware/decorator for access tokens in `app.py`.
- [ ] Add minimal JWT endpoints (`/api/login`, `/api/refresh`) needed for JWT auth.
- [ ] Add session endpoints:
  - [ ] GET `/sessions`
  - [ ] DELETE `/sessions/:id`
  - [ ] DELETE `/sessions/others`
- [ ] Integrate replay-detection compromise with session rows (`auth/rotation_service.py`).

## Phase 3 - Testing & QA
- [ ] Update/extend refresh rotation tests for session compromise.
- [ ] Add unit tests for session listing/revocation/ownership.
- [ ] Add integration tests: login → refresh → list → revoke.

## Phase 4 - CI/CD & Vercel
- [ ] Run `pytest` (all tests + coverage).
- [ ] Run `python app.py` smoke test.
- [ ] Verify endpoints work in Vercel/serverless-compatible mode.

