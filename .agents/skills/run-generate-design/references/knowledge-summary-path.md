# Knowledge Summary Path

The knowledge base summary file depends on the current agent locale:

| Locale | Summary file path |
|---|---|
| `sk` | `agent/knowledge/trusses-ai-slovak/summary.md` |
| `en` | `agent/knowledge/trusses-ai-english/summary.md` |

When the intent is `knowledge-query/summary`, read the summary file matching
the current locale and return its full contents as the tool output.
