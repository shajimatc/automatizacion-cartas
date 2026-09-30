import re
import zipfile
from pathlib import Path


template_path = Path(
    "app/templates/A/inicio/socios/"
    "A Inicio Socios TEMPLATE.docx"
)

temporary_path = template_path.with_name(
    "A Inicio Socios TEMPLATE limpio.docx"
)


with zipfile.ZipFile(
    template_path,
    "r",
) as original_zip:

    with zipfile.ZipFile(
        temporary_path,
        "w",
    ) as new_zip:

        for item in original_zip.infolist():

            data = original_zip.read(
                item.filename
            )

            if (
                item.filename.startswith("word/")
                and item.filename.endswith(".xml")
            ):
                data = re.sub(
                    rb"<w:highlight\b[^>]*/>",
                    b"",
                    data,
                )

            new_zip.writestr(
                item,
                data,
            )


print("Plantilla limpia creada correctamente.")
print(temporary_path)