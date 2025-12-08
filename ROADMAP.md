# Strategic ROADMAP.md

This is a living document that balances **Innovation**, **Stability**, and **Debt** for the Gemini CLI Helper (V3.0).

---

## 🏁 Phase 0: The Core (Stability & Debt)
**Goal**: Solid foundation.
- [ ] **Testing**: Coverage > 85%. `[Debt]` (Size: M)
- [ ] **CI/CD**: Enforce Linting (ruff) & Type Checking (mypy). `[Debt]` (Size: S)
- [ ] **Documentation**: Comprehensive README, Man pages, and API docs. `[Debt]` (Size: M)
- [ ] **Refactoring**: Replace raw `subprocess` calls with safe wrappers. `[Debt]` (Size: L)
- [ ] **Refactoring**: Fix `os.path` mocking strategies in tests. `[Debt]` (Size: L)

## 🚀 Phase 1: The Standard (Feature Parity)
**Goal**: Competitiveness.
- [ ] **UX**: Enhanced TUI (Dashboards, Progress Bars, Tables). `[Feat]` (Size: M) *Requires Phase 0*
- [x] **Config**: Configuration Profiles (Work/Personal). `[Feat]` (Size: S)
- [ ] **Config**: Robust Settings Management & Validation. `[Feat]` (Size: S)
- [ ] **Performance**: Async/Parallel Operations Refactor. `[Feat]` (Size: L)
- [ ] **Error Handling**: Standardized Error Codes & Telemetry. `[Feat]` (Size: M)
- [x] **Cloud**: Multi-Cloud Support (AWS S3). `[Feat]` (Size: L)

## 🔌 Phase 2: The Ecosystem (Integration)
**Goal**: Interoperability.
- [ ] **API**: REST API Server for remote management. `[Feat]` (Size: L) *Requires Phase 1*
- [ ] **Plugins**: Extension System (Hooks). `[Feat]` (Size: L) *Requires Phase 1*
- [ ] **SDK**: Python SDK (`import geminiai`). `[Feat]` (Size: M)
- [ ] **Webhooks**: Notification System (Slack/Discord). `[Feat]` (Size: S)

## 🔮 Phase 3: The Vision (Innovation)
**Goal**: Market Leader.
- [ ] **AI**: LLM Integration (Natural Language Command Interface). `[Feat]` (Size: XL) *Requires Phase 2*
- [ ] **Cloud**: Docker Container & K8s Support. `[Feat]` (Size: M)
- [ ] **AI**: Predictive Rate Limiting. `[Feat]` (Size: L)
- [ ] **Security**: Quantum-Resistant Encryption. `[Feat]` (Size: L)
