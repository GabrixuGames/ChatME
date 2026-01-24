# Changelog

## 2026-01-24
- Removed legacy/debug scripts and unused modules in backend.
- Removed unused validation module and tests.
- Split `app.py` routes and Socket.IO handlers into modules.
- Added service proxies on `app` to keep tests mocking working.
- Cleaned test warnings and stabilized auth integration tests.
- Updated security documentation to reflect removed migration scripts.

## 2026-01-25
- Consolidated documentation under `docs/` and simplified `README.md`.
- Cleaned backend imports and standardized DB resource handling.
- Refactored chat UI to support dual windows, drag-and-drop, and close behavior.
- Added mobile profile landing with friends/rooms accordions; improved desktop profile view.
- Simplified client auth routing and updated build/lint tooling.
- Removed unused frontend components, legacy private chat files, and unused UI modules.
- Added code-splitting in Vite build configuration.
