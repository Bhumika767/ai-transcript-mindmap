from html import escape

MERMAID_SCRIPT_URL = "https://cdn.jsdelivr.net/npm/mermaid@11/dist/mermaid.esm.min.mjs"


def render_mermaid_html(mermaid_definition: str) -> str:
    """Create a browser-openable HTML document from an existing Mermaid definition."""
    escaped_definition = escape(mermaid_definition, quote=False)
    return f'''<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>PDF Mind Map</title>
</head>
<body>
  <pre class="mermaid">{escaped_definition}</pre>
  <script type="module">
    import mermaid from "{MERMAID_SCRIPT_URL}";
    mermaid.initialize({{ startOnLoad: true }});
  </script>
</body>
</html>
'''
