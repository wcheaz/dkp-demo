# Knowledge Base Search Reference

## Locale-aware knowledge base selection

The knowledge base directory depends on the current agent locale (`sk` or `en`):

| Locale | Knowledge base directory | Summary file |
|---|---|---|
| `sk` | `agent/knowledge/trusses-ai-slovak/` | `agent/knowledge/trusses-ai-slovak/summary.md` |
| `en` | `agent/knowledge/trusses-ai-english/` | `agent/knowledge/trusses-ai-english/summary.md` |

Both directories contain the same 33 project subdirectories. The Slovak directory
contains original Slovak-language documents; the English directory contains
English translations. Always use the directory that matches the current locale.

## Scoring Algorithm

For each user query:

1. Split the query into lowercase words.
2. For each of the 33 project subdirectories:
   - **Name score**: Count how many query words appear in the subdirectory name
     (case-insensitive). Award 2 points per matching word.
   - **Section score**: Find the subdirectory's section in `summary.md`
     (marked by `### {subdir-name}`). Count how many query words appear in that
     section's text. Award 1 point per matching word.
   - **Total score** = name_score * 2 + section_score

3. Sort all subdirectories by total score (descending).
4. Select the top 3 scoring subdirectories.
5. Read all `.md` files within each selected subdirectory (recursive).
6. Format each document with a source header:

```
--- Source: knowledge/{kb-dir}/{subdir-name}/{file}.md ---
{file contents}
```

Where `{kb-dir}` is `trusses-ai-slovak` or `trusses-ai-english` based on locale.

## Fallback

If no subdirectory scores above zero, use the first 3 subdirectories
alphabetically.

## Source Citation Format

When citing sources in the final response, use the relative file path from the
knowledge base directory matching the current locale:

```
Source: knowledge/trusses-ai-slovak/{subdir}/{file}.md   (locale sk)
Source: knowledge/trusses-ai-english/{subdir}/{file}.md  (locale en)
```
