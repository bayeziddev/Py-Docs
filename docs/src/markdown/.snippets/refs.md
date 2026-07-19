mkdir -p docs/src/markdown/.snippets cat > docs/src/markdown/.snippets/refs.md <<'MD'

<!-- refs.md: references appended to pages automatically by pymdownx.snippets --> <!-- Add any reference snippets required by your docs here. -->
MD git add docs/src/markdown/.snippets/refs.md git commit -m "Add refs.md snippet required by build" git push