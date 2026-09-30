from app.modules.process_a.model import ProcessAData


def validate_process_a(data: ProcessAData):
    errors = []

    if not data.request_file:
        errors.append(
            "Debe seleccionar una Solicitud de Cotización."
        )

    if not data.cite_number.strip():
        errors.append("Debe ingresar el número de CITE.")

    if not data.cite_year.strip():
        errors.append("Debe ingresar el año del CITE.")
    elif len(data.cite_year) != 4 or not all(
        digit in "0123456789" for digit in data.cite_year
    ):
        errors.append("El año del CITE debe tener exactamente 4 dígitos numéricos.")

    if not data.stage:
        errors.append(
            "Debe seleccionar si la carta corresponde a Inicio o Fin."
        )

    if data.stage == "inicio":

        if not data.destination:
            errors.append(
                "Debe seleccionar el destino de la carta."
            )

        if data.destination == "socios":

            if not data.company_ids:
                errors.append(
                    "Debe seleccionar una empresa destinataria."
                )
            if not data.area_ids:
                errors.append(
                    "Debe seleccionar al menos un área."
                )

            if not data.billing_type:
                errors.append(
                    "Debe seleccionar el tipo de facturación."
                )

            if data.billing_type == "por_bloque":

                if not data.block_percentages:
                    errors.append(
                        "Debe ingresar los porcentajes por área."
                    )

                else:
                    missing_percentage = False
                    total_percentage = 0.0

                    for area_id in data.area_ids:
                        if area_id not in data.block_percentages:
                            missing_percentage = True
                            break

                        value = data.block_percentages[
                            area_id
                        ]

                        try:
                            percentage = float(
                                value.replace(",", ".")
                            )
                        except ValueError:
                            errors.append(
                                "Todos los porcentajes deben ser números."
                            )
                            break

                        if percentage < 0:
                            errors.append(
                                "Los porcentajes no pueden ser negativos."
                            )
                            break

                        total_percentage += percentage

                    if missing_percentage:
                        errors.append(
                            "Debe completar el porcentaje de todas las áreas seleccionadas."
                        )

                    elif not errors and abs(
                        total_percentage - 100
                    ) > 0.01:
                        errors.append(
                            "La suma de los porcentajes debe ser 100%."
                        )

        if data.destination == "ypfb":

            if not data.area_ids:
                errors.append(
                    "Debe seleccionar al menos un área."
                )

    if data.stage == "fin":
        if not data.area_ids:
            errors.append("Debe seleccionar al menos un área.")
        if not data.authorization_reference.strip():
            errors.append("Debe ingresar la referencia de autorización.")
        if not data.sincop_registration.strip():
            errors.append("Debe ingresar el registro SINCOP.")

    return errors
