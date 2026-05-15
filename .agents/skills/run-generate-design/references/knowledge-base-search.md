# Knowledge Base Search Reference

The knowledge base lives at `agent/knowledge/trusses-ai-english/` and contains
33 project subdirectories plus a top-level `summary.md`.

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
--- Source: knowledge/trusses-ai-english/{subdir-name}/{file}.md ---
{file contents}
```

## Fallback

If no subdirectory scores above zero, use the first 3 subdirectories
alphabetically.

## Source Citation Format

When citing sources in the final response, use the relative file path from the
knowledge base directory:

```
Source: knowledge/trusses-ai-english/{subdir}/{file}.md
```

## Knowledge Summary Path

The overview summary is at:
`agent/knowledge/trusses-ai-english/summary.md`
