from html import escape
from pathlib import Path


EVIDENCE_DIR = Path("evidencias")


HTML_TEMPLATE = """<!doctype html>
<html lang="es">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{title}</title>
  <style>
    body {{
      margin: 0;
      background: #0f172a;
      color: #e2e8f0;
      font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", monospace;
    }}
    main {{
      padding: 28px;
    }}
    h1 {{
      margin: 0 0 18px;
      font-family: Arial, Helvetica, sans-serif;
      font-size: 28px;
      letter-spacing: 0;
    }}
    pre {{
      white-space: pre-wrap;
      background: #020617;
      border: 1px solid #334155;
      border-radius: 8px;
      padding: 20px;
      font-size: 14px;
      line-height: 1.45;
    }}
  </style>
</head>
<body>
  <main>
    <h1>{title}</h1>
    <pre>{content}</pre>
  </main>
</body>
</html>
"""


def write_page(source: Path, target: Path, title: str) -> None:
    text = source.read_text(encoding="utf-8")
    target.write_text(
        HTML_TEMPLATE.format(title=escape(title), content=escape(text)),
        encoding="utf-8",
    )


def main() -> None:
    write_page(
        EVIDENCE_DIR / "docker_terminal.txt",
        EVIDENCE_DIR / "docker_terminal.html",
        "Evidencia Docker Compose y contenedor activo",
    )
    write_page(
        EVIDENCE_DIR / "load_postgres.txt",
        EVIDENCE_DIR / "load_postgres.html",
        "Evidencia carga PostgreSQL",
    )
    print("created evidence html pages")


if __name__ == "__main__":
    main()

