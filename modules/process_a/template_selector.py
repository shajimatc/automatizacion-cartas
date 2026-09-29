from pathlib import Path

from app.modules.process_a.model import ProcessAData


TEMPLATES_DIR = (
    Path(__file__).resolve().parent.parent.parent
    / "templates"
    / "A"
)


def select_process_a_template(data: ProcessAData):
    if data.stage == "inicio":

        if data.destination == "ypfb":
            return (
                TEMPLATES_DIR
                / "inicio"
                / "ypfb"
                / "A Inicio YPFB TEMPLATE.docx"
            )

        if data.destination == "socios":
            return (
                TEMPLATES_DIR
                / "inicio"
                / "socios"
                / "A Inicio Socios TEMPLATE.docx"
            )

    if data.stage == "fin":
        return (
            TEMPLATES_DIR
            / "fin"
            / "A Remito YPFB.docx"
        )

    return None