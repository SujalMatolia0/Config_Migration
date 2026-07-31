# Workspace Rules & Constraints

## No Emojis Rule
- Do NOT use emojis anywhere in the project (code, comments, documentation, UI, logs, generated reports, CLI output, or markdown artifacts).
- Use clean text tags (e.g. `[PDF]`, `[SUCCESS]`, `[WARNING]`, `[ERROR]`, `[TabSet]`) or standard SVG/Font icons where icons are needed.

## Universal Parser Fallback & Unhandled Schema Safeguard Rule
- Every XML/code parser MUST implement a robust fallback mechanism for unhandled, novel, or cross-component XML tags.
- Child XML tags MUST be cross-checked against known schemas across all OSVC components (Workspaces, Analytics Reports, CPM Procedures, Business Rules, Navigation Sets, BUI Add-Ins).
- If an XML element cannot be parsed into a specialized domain model, it MUST NOT be silently ignored or discarded. It MUST be captured in an `unhandled_elements` manifest and rendered as a formatted callout alert (`> [!WARNING] Unhandled Schema Element`) with its tag name and raw snippet in the report documentation.

