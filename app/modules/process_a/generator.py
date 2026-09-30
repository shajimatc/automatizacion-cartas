from pathlib import Path

from docxtpl import DocxTemplate

from app.modules.process_a.mapper import map_process_a_data
from app.modules.process_a.template_selector import (
    select_process_a_template,
)
from app.modules.process_a.model import ProcessAData


def generate_process_a_document(
    data: ProcessAData,
    output_path: str,
):
    template_path = select_process_a_template(
        data
    )

    if template_path is None:
        raise ValueError(
            "No se encontró una plantilla para esta combinación."
        )

    if not Path(template_path).exists():
        raise FileNotFoundError(
            f"No existe la plantilla: {template_path}"
        )

    context = map_process_a_data(
        data
    )

    document = DocxTemplate(
        str(template_path)
    )

    document.render(
        context
    )

    document.save(
        output_path
    )

    return output_path