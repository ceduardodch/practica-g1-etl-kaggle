from pathlib import Path
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Image,
    PageBreak,
    Table,
    TableStyle,
)


REPORT_PATH = Path("output/pdf/informe_practica_g1.pdf")
EVIDENCE_DIR = Path("evidencias")


def add_image(story, image_path: Path, caption: str) -> None:
    styles = getSampleStyleSheet()
    story.append(Paragraph(caption, styles["Heading3"]))
    if image_path.exists():
        img = Image(str(image_path))
        max_width = 6.8 * inch
        max_height = 4.4 * inch
        scale = min(max_width / img.imageWidth, max_height / img.imageHeight)
        img.drawWidth = img.imageWidth * scale
        img.drawHeight = img.imageHeight * scale
        story.append(img)
    else:
        story.append(Paragraph(f"No se encontro la imagen: {image_path}", styles["BodyText"]))
    story.append(Spacer(1, 0.18 * inch))


def main() -> None:
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name="Small", parent=styles["BodyText"], fontSize=8, leading=10))

    doc = SimpleDocTemplate(
        str(REPORT_PATH),
        pagesize=letter,
        rightMargin=0.55 * inch,
        leftMargin=0.55 * inch,
        topMargin=0.55 * inch,
        bottomMargin=0.55 * inch,
    )

    story = []
    story.append(Paragraph("Informe Practica G1 - ETL de Ciberseguridad", styles["Title"]))
    story.append(Spacer(1, 0.2 * inch))
    story.append(
        Paragraph(
            "Dominio seleccionado: ciberseguridad y monitoreo de incidentes de red. La data fue tomada desde Kaggle Search usando el dataset publico Cyber Security Attacks.",
            styles["BodyText"],
        )
    )
    story.append(Spacer(1, 0.2 * inch))

    data = [
        ["Entregable", "Archivo"],
        ["Compose", "docker-compose.yml"],
        ["Variables", ".env"],
        ["Notebook S1", "desarrolloG1.ipynb"],
        ["Notebook S2", "TransformG1.ipynb"],
        ["Evidencias", "evidencias/*.png"],
        ["Reporte", "output/pdf/informe_practica_g1.pdf"],
    ]
    table = Table(data, colWidths=[1.7 * inch, 4.8 * inch])
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1f2937")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("GRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#cbd5e1")),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("PADDING", (0, 0), (-1, -1), 6),
            ]
        )
    )
    story.append(table)
    story.append(PageBreak())

    story.append(Paragraph("Evidencias de ejecucion", styles["Heading1"]))
    evidence = [
        ("01_kaggle_search.png", "Captura 1. Busqueda en Kaggle del dataset de ciberseguridad."),
        ("02_docker_terminal.png", "Captura 2. Ejecucion exitosa de Docker Compose y contenedor PostgreSQL activo."),
        ("03_notebook_html.png", "Captura 3. Notebook Semana 1 ejecutado con DataFrames y analisis."),
        ("05_transform_notebook_html.png", "Captura 4. Notebook Semana 2 ejecutado con limpieza y transformacion."),
        ("04_github_repo.png", "Captura 5. Repositorio publico creado en GitHub."),
    ]
    for filename, caption in evidence:
        add_image(story, EVIDENCE_DIR / filename, caption)

    story.append(PageBreak())
    story.append(Paragraph("Resumen tecnico", styles["Heading1"]))
    story.append(
        Paragraph(
            "El flujo descarga datos de ciberseguridad desde Kaggle, genera un inventario CSV y un catalogo JSON, carga la tabla de hechos network_alerts en PostgreSQL y analiza tres DataFrames: PostgreSQL, CSV y JSON. El notebook de Semana 1 cubre primeras filas, nulos, faltantes, estadisticos y agrupaciones. El notebook de Semana 2 cubre exploracion, variables de entorno, limpieza, seleccion de columnas, transformaciones, identificadores y validacion final.",
            styles["BodyText"],
        )
    )
    story.append(Spacer(1, 0.2 * inch))
    story.append(
        Paragraph(
            "Las reflexiones profesionales solicitadas se encuentran al final de `desarrolloG1.ipynb` y `TransformG1.ipynb`.",
            styles["BodyText"],
        )
    )

    doc.build(story)
    print(f"created {REPORT_PATH}")


if __name__ == "__main__":
    main()
