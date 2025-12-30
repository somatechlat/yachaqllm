# VIBE CODING RULES

## Herramientas Prohibidas
- ❌ **browser_subagent** - NO USAR
- ❌ **Vision Agent** - NO USAR

## Herramientas Permitidas para Web
- ✅ **curl** - Para descargas directas
- ✅ **Playwright** - Para navegación automatizada
- ✅ **wget** - Para descargas
- ✅ **read_url_content** - Para leer contenido web

---

## ⚡ VIBE CODING RULES ⚡

### 1. NO BULLSHIT
- NO lies, NO guesses, NO invented APIs
- NO mocks, NO placeholders, NO fake functions
- Say EXACTLY what is true

### 2. CHECK FIRST, CODE SECOND
- ALWAYS review existing architecture BEFORE writing code
- NEVER assume - VERIFY

### 3. NO UNNECESSARY FILES
- Modify existing files unless new file is unavoidable
- Simplicity > complexity

### 4. REAL IMPLEMENTATIONS ONLY
- Everything must be production-grade
- NO fake returns, NO hardcoded values

### 5. DOCUMENTATION = TRUTH
- Always read documentation PROACTIVELY
- NEVER invent API syntax
- Cite documentation

### 6. COMPLETE CONTEXT REQUIRED
- Understand data flow, dependencies, impact
- If context missing → ASK FIRST

### 7. REAL DATA & SERVERS ONLY
- Use real data structures
- NO assumptions, NO hallucinated structures

---

## Framework Policies

### API: Django + Django Ninja ONLY
- NO FastAPI

### UI: Lit Web Components ONLY
- NO Alpine.js

### Database: Django ORM ONLY
- NO SQLAlchemy for new models

### Messages: Centralized I18N
- Use `get_message(code, **kwargs)`
- NO hardcoded strings
