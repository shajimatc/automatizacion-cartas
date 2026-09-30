from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QLineEdit,
    QFileDialog,
    QRadioButton,
    QButtonGroup,
    QFrame,
    QComboBox,
    QScrollArea,
    QCheckBox,
    QMessageBox,
    QDialog,
    QDialogButtonBox,
    QTextEdit,
)
from app.services.catalog_service import (
    load_companies,
    load_areas,
)

from app.modules.process_a.model import ProcessAData
from app.modules.process_a.validator import validate_process_a
from app.modules.process_a.mapper import map_process_a_data
from app.modules.process_a.generator import generate_process_a_document
from app.services.request_extractor import (
    extract_request_number,
    extract_process_description,
    extract_request_annexes,
)

class OptionCheckBox(QCheckBox):
    def hitButton(self, position):
        return self.rect().contains(position)


class OptionRadioButton(QRadioButton):
    def hitButton(self, position):
        return self.rect().contains(position)


class ProcessAPage(QWidget):
    back_requested = Signal()

    def __init__(self):
        super().__init__()

        self.selected_file_path = ""
        self.data = ProcessAData()

        self.setup_ui()
    def setup_ui(self):
        self.setObjectName("processAPage")
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(60, 40, 60, 40)
        main_layout.setSpacing(20)

        # -----------------------------
        # ENCABEZADO
        # -----------------------------

        header_layout = QHBoxLayout()

        back_button = QPushButton("← Volver")
        back_button.setObjectName("secondaryButton")
        back_button.clicked.connect(self.back_requested.emit)

        header_layout.addWidget(back_button)
        header_layout.addStretch()

        main_layout.addLayout(header_layout)

        title = QLabel("Proceso A")
        title.setObjectName("pageTitle")

        subtitle = QLabel(
            "Complete los datos iniciales para comenzar la generación de la carta."
        )
        subtitle.setObjectName("pageSubtitle")

        main_layout.addWidget(title)
        main_layout.addWidget(subtitle)

        # -----------------------------
        # TARJETA PRINCIPAL
        # -----------------------------

        form_card = QFrame()
        form_card.setObjectName("formCard")

        form_layout = QVBoxLayout(form_card)
        form_layout.setContentsMargins(30, 30, 30, 30)
        form_layout.setSpacing(20)

        # -----------------------------
        # 1. SOLICITUD DE COTIZACIÓN
        # -----------------------------

        request_title = QLabel("1. Solicitud de Cotización")
        request_title.setObjectName("sectionTitle")

        request_description = QLabel(
            "Seleccione el archivo de Solicitud de Cotización correspondiente al proceso."
        )
        request_description.setObjectName("fieldDescription")

        self.file_label = QLabel("Ningún archivo seleccionado")
        self.file_label.setObjectName("fileStatus")

        select_file_button = QPushButton("Seleccionar archivo")
        select_file_button.clicked.connect(self.select_request_file)

        form_layout.addWidget(request_title)
        form_layout.addWidget(request_description)
        form_layout.addWidget(self.file_label)
        form_layout.addWidget(select_file_button)

        # -----------------------------
        # 2. CITE
        # -----------------------------

        cite_title = QLabel("2. CITE de la carta")
        cite_title.setObjectName("sectionTitle")

        cite_description = QLabel(
            "Ingrese el identificador CITE que tendrá la carta."
        )
        cite_description.setObjectName("fieldDescription")

        self.cite_input = QLineEdit()
        self.cite_input.setPlaceholderText(
            "Ejemplo: CITE correspondiente a la carta"
        )

        form_layout.addWidget(cite_title)
        form_layout.addWidget(cite_description)
        form_layout.addWidget(self.cite_input)

        # -----------------------------
        # 3. ETAPA DEL PROCESO
        # -----------------------------

        stage_title = QLabel("3. Etapa del proceso")
        stage_title.setObjectName("sectionTitle")

        stage_description = QLabel(
            "Seleccione si la carta corresponde al inicio o al fin del proceso."
        )
        stage_description.setObjectName("fieldDescription")

        stage_layout = QHBoxLayout()

        self.start_radio = OptionRadioButton("Inicio")
        self.end_radio = OptionRadioButton("Fin")

        self.stage_group = QButtonGroup(self)
        self.stage_group.addButton(self.start_radio)
        self.stage_group.addButton(self.end_radio)

        stage_layout.addWidget(self.start_radio)
        stage_layout.addWidget(self.end_radio)
        stage_layout.addStretch()

        form_layout.addWidget(stage_title)
        form_layout.addWidget(stage_description)
        form_layout.addLayout(stage_layout)

        # -----------------------------
        # 4. DESTINO DE LA CARTA
        # -----------------------------

        self.destination_frame = QFrame()
        self.destination_frame.setObjectName("dynamicSection")

        destination_layout = QVBoxLayout(self.destination_frame)
        destination_layout.setContentsMargins(20, 20, 20, 20)
        destination_layout.setSpacing(12)

        destination_title = QLabel("4. Destino de la carta")
        destination_title.setObjectName("sectionTitle")

        destination_description = QLabel(
            "Seleccione a quién estará dirigida la carta de inicio."
        )
        destination_description.setObjectName("fieldDescription")

        destination_options_layout = QHBoxLayout()

        self.partners_radio = OptionRadioButton("Socios / Empresas")
        self.ypfb_radio = OptionRadioButton("YPFB")

        self.destination_group = QButtonGroup(self)
        self.destination_group.addButton(self.partners_radio)
        self.destination_group.addButton(self.ypfb_radio)

        destination_options_layout.addWidget(self.partners_radio)
        destination_options_layout.addWidget(self.ypfb_radio)
        destination_options_layout.addStretch()

        destination_layout.addWidget(destination_title)
        destination_layout.addWidget(destination_description)
        destination_layout.addLayout(destination_options_layout)

        form_layout.addWidget(self.destination_frame)

        self.destination_frame.hide()

        # -----------------------------
        # 5A. SOCIOS / EMPRESAS
        # -----------------------------

        self.partners_frame = QFrame()
        self.partners_frame.setObjectName("dynamicSection")

        partners_layout = QVBoxLayout(self.partners_frame)
        partners_layout.setContentsMargins(20, 20, 20, 20)
        partners_layout.setSpacing(15)

        partners_title = QLabel("5. Datos para Socios")
        partners_title.setObjectName("sectionTitle")

        partners_description = QLabel(
            "Seleccione la empresa destinataria y el tipo de facturación."
        )
        partners_description.setObjectName("fieldDescription")

        company_label = QLabel("Empresa destinataria")
        company_label.setObjectName("fieldLabel")


        companies_label = QLabel("Empresas destinatarias")
        companies_label.setObjectName("fieldLabel")

        self.company_checkboxes = []

        self.companies = load_companies()
        self.areas = load_areas()

        partners_layout.addWidget(partners_title)
        partners_layout.addWidget(partners_description)

        partners_layout.addWidget(companies_label)

        for company in self.companies:
            checkbox = OptionCheckBox(company["company"])

            checkbox.setProperty(
                "company_id",
                company["id"],
            )

            self.company_checkboxes.append(
                checkbox
            )

            partners_layout.addWidget(
                checkbox
            )

        partner_areas_label = QLabel("Áreas relacionadas")
        partner_areas_label.setObjectName("fieldLabel")

        self.partner_area_checkboxes = []

        partners_layout.addWidget(
            partner_areas_label
        )

        for area in self.areas:
            checkbox = OptionCheckBox(area["name"])

            checkbox.setProperty(
                "area_id",
                area["id"],
            )

            self.partner_area_checkboxes.append(
                checkbox
            )
            checkbox.stateChanged.connect(
                self.update_block_percentage_inputs
            )
            partners_layout.addWidget(
                checkbox
            )
            
        billing_label = QLabel("Tipo de facturación")
        billing_label.setObjectName("fieldLabel")

        billing_options_layout = QVBoxLayout()

        self.tcs_radio = OptionRadioButton("TCS")
        self.framework_radio = OptionRadioButton("Contrato Marco")
        self.block_radio = OptionRadioButton("Distribución por bloque")

        self.billing_group = QButtonGroup(self)
        self.billing_group.addButton(self.tcs_radio)
        self.billing_group.addButton(self.framework_radio)
        self.billing_group.addButton(self.block_radio)

        billing_options_layout.addWidget(self.tcs_radio)
        billing_options_layout.addWidget(self.framework_radio)
        billing_options_layout.addWidget(self.block_radio)

        partners_layout.addWidget(billing_label)
        partners_layout.addLayout(billing_options_layout)

        # -----------------------------
        # PORCENTAJES POR BLOQUE
        # -----------------------------

        self.block_frame = QFrame()
        self.block_frame.setObjectName("subSection")

        block_layout = QVBoxLayout(self.block_frame)
        block_layout.setContentsMargins(15, 15, 15, 15)
        block_layout.setSpacing(10)

        block_title = QLabel("Distribución porcentual por bloque")
        block_title.setObjectName("fieldLabel")

        block_description = QLabel(
            "Ingrese el porcentaje correspondiente "
            "para cada área seleccionada."
        )
        block_description.setObjectName("fieldDescription")

        self.block_percentage_inputs = {}

        self.block_inputs_container = QFrame()
        self.block_inputs_layout = QVBoxLayout(
            self.block_inputs_container
        )

        self.block_inputs_layout.setContentsMargins(
            0,
            0,
            0,
            0,
        )

        self.block_inputs_layout.setSpacing(10)

        block_layout.addWidget(block_title)
        block_layout.addWidget(block_description)
        block_layout.addWidget(
            self.block_inputs_container
        )

        partners_layout.addWidget(self.block_frame)

        form_layout.addWidget(self.partners_frame)

        self.partners_frame.hide()
        self.block_frame.hide()

        # -----------------------------
        # 5B. YPFB
        # -----------------------------

        self.ypfb_frame = QFrame()
        self.ypfb_frame.setObjectName("dynamicSection")

        ypfb_layout = QVBoxLayout(self.ypfb_frame)
        ypfb_layout.setContentsMargins(20, 20, 20, 20)
        ypfb_layout.setSpacing(15)

        ypfb_title = QLabel("5. Datos para YPFB")
        ypfb_title.setObjectName("sectionTitle")

        ypfb_description = QLabel(
            "Seleccione las áreas relacionadas con el proceso."
        )
        ypfb_description.setObjectName("fieldDescription")

        areas_label = QLabel("Áreas")
        areas_label.setObjectName("fieldLabel")

        ypfb_layout.addWidget(ypfb_title)
        ypfb_layout.addWidget(ypfb_description)
        ypfb_layout.addWidget(areas_label)

        self.area_checkboxes = []

        self.areas = load_areas()

        for area in self.areas:
            checkbox = OptionCheckBox(area["name"])

            checkbox.setProperty(
                "area_id",
                area["id"],
            )

            self.area_checkboxes.append(
                checkbox
            )

            ypfb_layout.addWidget(
                checkbox
            )

        form_layout.addWidget(self.ypfb_frame)

        self.ypfb_frame.hide()

        self.close_frame = QFrame()
        self.close_frame.setObjectName("dynamicSection")
        close_layout = QVBoxLayout(self.close_frame)
        close_layout.setContentsMargins(20, 20, 20, 20)
        close_layout.setSpacing(12)
        close_title = QLabel("6. Datos de cierre — Destino: YPFB")
        close_title.setObjectName("sectionTitle")
        close_layout.addWidget(close_title)
        close_layout.addWidget(QLabel("Referencia de autorización"))
        self.authorization_reference_input = QLineEdit()
        self.authorization_reference_input.setPlaceholderText("CEAC-123/2026")
        close_layout.addWidget(self.authorization_reference_input)
        close_layout.addWidget(QLabel("Registro SINCOP"))
        self.sincop_registration_input = QLineEdit()
        self.sincop_registration_input.setPlaceholderText("PEB-A-012/2026")
        close_layout.addWidget(self.sincop_registration_input)
        form_layout.addWidget(self.close_frame)
        self.close_frame.hide()

        # -----------------------------
        # CONEXIÓN DE LA LÓGICA
        # -----------------------------

        self.start_radio.toggled.connect(
            self.update_stage_options
        )

        self.end_radio.toggled.connect(
            self.update_stage_options
        )

        self.partners_radio.toggled.connect(
            self.update_destination_options
        )

        self.ypfb_radio.toggled.connect(
            self.update_destination_options
        )

        self.block_radio.toggled.connect(
            self.update_billing_options
        )

        # -----------------------------
        # SCROLL
        # -----------------------------

        preview_button = QPushButton("Revisar datos")
        preview_button.clicked.connect(
            self.show_preview
        )

        form_layout.addWidget(
            preview_button
        )

        generate_button = QPushButton("Generar Word")
        generate_button.clicked.connect(
            self.generate_test_document
        )

        form_layout.addWidget(
            generate_button

        )        
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.NoFrame)
        scroll_area.setWidget(form_card)

        main_layout.addWidget(scroll_area)

    def select_request_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Seleccionar Solicitud de Cotización",
            "",
            "Documentos (*.docx *.doc *.pdf);;Todos los archivos (*.*)",
        )

        if file_path:
            self.selected_file_path = file_path
            self.file_label.setText(file_path)

    def update_stage_options(self):
        self.close_frame.setVisible(self.end_radio.isChecked())
        if self.start_radio.isChecked():
            self.destination_frame.show()
            self.update_destination_options()

        else:
            self.destination_frame.hide()
            self.partners_frame.hide()
            self.ypfb_frame.hide()
            self.block_frame.hide()

            self.destination_group.setExclusive(False)
            self.partners_radio.setChecked(False)
            self.ypfb_radio.setChecked(False)
            self.destination_group.setExclusive(True)
            self.ypfb_frame.setVisible(self.end_radio.isChecked())

    def update_destination_options(self):
        if self.end_radio.isChecked():
            self.partners_frame.hide()
            self.block_frame.hide()
            self.ypfb_frame.show()
            return
        if self.partners_radio.isChecked():
            self.partners_frame.show()
            self.ypfb_frame.hide()

        elif self.ypfb_radio.isChecked():
            self.partners_frame.hide()
            self.block_frame.hide()
            self.ypfb_frame.show()

        else:
            self.partners_frame.hide()
            self.ypfb_frame.hide()
            self.block_frame.hide()

    def update_billing_options(self):
        if self.block_radio.isChecked() and self.start_radio.isChecked():
            self.block_frame.show()

        else:
            self.block_frame.hide()

    def collect_form_data(self):
        self.data.request_file = self.selected_file_path
        self.data.annexes = []
        if self.data.request_file:
            self.data.process_number = (
                extract_request_number(
                    self.data.request_file
                )
            )

            self.data.process_description = (
                extract_process_description(
                    self.data.request_file
                )
            )
            self.data.annexes = extract_request_annexes(
                self.data.request_file
            )
        self.data.cite = self.cite_input.text().strip()

        if self.start_radio.isChecked():
            self.data.stage = "inicio"
        elif self.end_radio.isChecked():
            self.data.stage = "fin"
        else:
            self.data.stage = ""

        if self.partners_radio.isChecked():
            self.data.destination = "socios"
        elif self.ypfb_radio.isChecked():
            self.data.destination = "ypfb"
        else:
            self.data.destination = ""

        selected_companies = []

        if self.partners_radio.isChecked():
            for checkbox in self.company_checkboxes:
                if checkbox.isChecked():
                    selected_companies.append(
                        checkbox.property("company_id")
                    )

        self.data.company_ids = selected_companies

        if self.tcs_radio.isChecked():
            self.data.billing_type = "tcs"
        elif self.framework_radio.isChecked():
            self.data.billing_type = "contrato_marco"
        elif self.block_radio.isChecked():
            self.data.billing_type = "por_bloque"
        else:
            self.data.billing_type = None

        block_percentages = {}

        if self.block_radio.isChecked():
            for area_id, input_field in (
                self.block_percentage_inputs.items()
            ):
                value = input_field.text().strip()

                if value:
                    block_percentages[
                        area_id
                    ] = value

        self.data.block_percentages = (
            block_percentages
        )

        selected_areas = []

        if self.partners_radio.isChecked():
            for checkbox in self.partner_area_checkboxes:
                if checkbox.isChecked():
                    selected_areas.append(
                        checkbox.property("area_id")
                    )

        elif self.ypfb_radio.isChecked():
            for checkbox in self.area_checkboxes:
                if checkbox.isChecked():
                    selected_areas.append(
                        checkbox.property("area_id")
                    )

        self.data.area_ids = selected_areas

        self.data.authorization_reference = ""
        self.data.sincop_registration = ""
        if self.data.stage == "fin":
            self.data.destination = "ypfb"
            self.data.company_ids = []
            self.data.billing_type = None
            self.data.block_percentages = {}
            self.data.block_distribution = ""
            self.data.annexes = []
            self.data.area_ids = [
                checkbox.property("area_id")
                for checkbox in self.area_checkboxes
                if checkbox.isChecked()
            ]
            self.data.authorization_reference = (
                self.authorization_reference_input.text().strip()
            )
            self.data.sincop_registration = (
                self.sincop_registration_input.text().strip()
            )

    def show_collected_data(self):
        pass

    def show_preview(self):
        self.collect_form_data()

        errors = validate_process_a(self.data)

        if errors:
            QMessageBox.warning(
                self,
                "Faltan datos",
                "\n".join(errors),
            )
            return

        mapped_data = map_process_a_data(self.data)

        areas_text = mapped_data.get("areas_text", "")
        cc_companies = mapped_data.get("cc_companies", [])

        cc_text = (
            "\n".join(cc_companies)
            if cc_companies
            else "Sin copias"
        )
        if self.data.destination == "socios":
            cc_text = "No aplica"

        billing_type = (
            self.data.billing_type
            if self.data.billing_type
            else "No aplica"
        )

        percentages_text = "No aplica"

        if self.data.block_percentages:
            percentage_lines = []

            for area in mapped_data.get("block_distribution", []):
                area_id = area["area_id"]
                area_name = area["area_name"]

                if area_id in self.data.block_percentages:
                    percentage = self.data.block_percentages[area_id]
                    percentage_lines.append(
                        f"{area_name}: {percentage}%"
                    )

            if percentage_lines:
                percentages_text = "\n".join(percentage_lines)

        annexes_text = (
            "\n".join(self.data.annexes)
            if self.data.annexes
            else "No se detectaron anexos o documentos"
        )

        preview_text = f"""
DATOS EXTRAÍDOS DE LA SOLICITUD

Número de proceso:
{self.data.process_number}

Descripción:
{self.data.process_description}


ANEXOS Y DOCUMENTOS DETECTADOS

{annexes_text}


DATOS SELECCIONADOS

CITE:
{self.data.cite}

Etapa:
{self.data.stage}

Destino:
{self.data.destination}

Áreas:
{areas_text}

Tipo de facturación:
{billing_type}

Distribución por área:
{percentages_text}


DATOS CALCULADOS AUTOMÁTICAMENTE

Fecha:
{mapped_data["current_day"]} de {mapped_data["current_month"]} de {mapped_data["current_year"]}

Copias:
{cc_text}
"""

        if self.data.stage == "fin":
            attachments_text = "\n".join(
                f"Anexo {index}: {attachment}"
                for index, attachment in enumerate(
                    mapped_data["close_attachments"], start=1
                )
            )
            preview_text = f"""
DATOS DE CIERRE — YPFB

Número de proceso:
{self.data.process_number}

Descripción:
{self.data.process_description}

CITE:
{self.data.cite}

Áreas:
{areas_text}

Referencia de autorización:
{self.data.authorization_reference}

Registro SINCOP:
{self.data.sincop_registration}

Fecha:
{mapped_data['current_day']} de {mapped_data['current_month']} de {mapped_data['current_year']}

Copias:
{cc_text}

ADJUNTOS DE CIERRE
{attachments_text}
"""

        dialog = QDialog(self)
        dialog.setWindowTitle("Previsualización de datos")
        dialog.resize(650, 600)

        layout = QVBoxLayout(dialog)

        title = QLabel(
            "Revise los datos antes de generar la carta"
        )
        layout.addWidget(title)

        preview_box = QTextEdit()
        preview_box.setReadOnly(True)
        preview_box.setPlainText(preview_text.strip())
        layout.addWidget(preview_box)

        buttons = QDialogButtonBox(QDialogButtonBox.Close)
        buttons.rejected.connect(dialog.reject)
        layout.addWidget(buttons)

        dialog.exec()

    def validate_form(self):
        self.collect_form_data()

        errors = validate_process_a(
            self.data
        )

        if errors:
            message = "\n".join(
                f"• {error}"
                for error in errors
            )

            QMessageBox.warning(
                self,
                "Datos incompletos",
                message,
            )

            return

        QMessageBox.information(
            self,
            "Validación correcta",
            "Los datos del Proceso A están completos.",
        )

    def show_mapped_data(self):
        self.collect_form_data()

        errors = validate_process_a(
            self.data
        )

        if errors:
            message = "\n".join(
                f"• {error}"
                for error in errors
            )

            QMessageBox.warning(
                self,
                "Datos incompletos",
                message,
            )

            return

        mapped_data = map_process_a_data(
            self.data
        )

        message = "\n".join(
            f"{key}: {value}"
            for key, value in mapped_data.items()
        )

        QMessageBox.information(
            self,
            "Datos preparados",
            message,
        )
    def generate_test_document(self):
        self.collect_form_data()

        errors = validate_process_a(
            self.data
        )

        if errors:
            message = "\n".join(
                f"• {error}"
                for error in errors
            )

            QMessageBox.warning(
                self,
                "Datos incompletos",
                message,
            )

            return

        output_path, _ = QFileDialog.getSaveFileName(
            self,
            "Guardar Word generado",
            "Carta_Proceso_A.docx",
            "Documento Word (*.docx)",
        )

        if not output_path:
            return

        try:
            generate_process_a_document(
                self.data,
                output_path,
            )

            QMessageBox.information(
                self,
                "Documento generado",
                "El documento Word fue generado correctamente.",
            )

        except Exception as error:
            QMessageBox.critical(
                self,
                "Error al generar",
                str(error),
            )

    def update_block_percentage_inputs(self):
        for i in reversed(
            range(self.block_inputs_layout.count())
        ):
            widget = (
                self.block_inputs_layout
                .itemAt(i)
                .widget()
            )

            if widget is not None:
                widget.deleteLater()

        self.block_percentage_inputs = {}

        for checkbox in self.partner_area_checkboxes:
            if checkbox.isChecked():
                area_id = checkbox.property("area_id")
                area_name = checkbox.text()

                row = QHBoxLayout()

                label = QLabel(area_name)

                percentage_input = QLineEdit()
                percentage_input.setPlaceholderText("0")
                percentage_input.setMaximumWidth(100)

                percent_label = QLabel("%")

                row.addWidget(label)
                row.addWidget(percentage_input)
                row.addWidget(percent_label)
                row.addStretch()

                row_container = QFrame()
                row_container.setLayout(row)

                self.block_inputs_layout.addWidget(
                    row_container
                )

                self.block_percentage_inputs[
                    area_id
                ] = percentage_input
