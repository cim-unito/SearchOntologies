import flet as ft

from model.metadata_container import MetadataContainer


class ViewOntology(ft.Control):
    COLUMN_WIDTHS = {
        "code": 130,
        "subdomain": 140,
        "value": 220,
        "ontology": 150,
        "synonyms": 200,
        "iri": 220,
    }

    def __init__(self, page: ft.Page):
        super().__init__()
        # page
        self._page = page
        self._page.title = "FoundingGIDE Ontology "
        self._page.horizontal_alignment = 'CENTER'
        self._page.theme_mode = ft.ThemeMode.DARK
        self._page.scroll = ft.ScrollMode.AUTO
        # controller (it is not initialized. Must be initialized in the main,
        # after the controller is created)
        self._controller = None
        # graphical elements
        self._title = None
        self.btn_select_file = None
        self.file_picker = None
        self.dt_metadata = None
        self.btn_search = None

    def load_interface(self):
        # title
        self._title = ft.Text("FoundingGIDE", color="blue", size=24)
        self._page.controls.append(self._title)

        # button select the metadata excel file
        self.file_picker = ft.FilePicker(on_result=self.on_file_picked)
        self._page.overlay.append(self.file_picker)
        self.btn_select_file = ft.ElevatedButton(
            text="Select the metadata excel file",
            icon=ft.Icons.FOLDER_OPEN,
            on_click=lambda _: self.file_picker.pick_files(
                allow_multiple=False,
                allowed_extensions=["xlsx"]
            )
        )
        self._page.controls.append(self.btn_select_file)

        # metadata table
        self.dt_metadata = ft.DataTable(
            columns=[
                self._build_column("Code", "code"),
                self._build_column("Subdomain", "subdomain"),
                self._build_column("Value", "value"),
                self._build_column("Ontology", "ontology"),
                self._build_column("Synonyms", "synonyms"),
                self._build_column("IRI", "iri"),
            ],
            rows=[],
            data_row_min_height=44,
            data_row_max_height=240,
        )
        table_width = sum(self.COLUMN_WIDTHS.values()) + 40
        self._page.controls.append(
            ft.Container(
                width=table_width,
                expand=True,
                content=ft.Column([
                    self.dt_metadata
                ], scroll=ft.ScrollMode.AUTO)
            )
        )

        # button select the metadata excel file
        self.btn_search = ft.ElevatedButton(
            text="Search",
            icon=ft.Icons.SEARCH,
            on_click=self._controller.lookup_term
        )
        self._page.controls.append(self.btn_search)

        self._page.update()

    def on_file_picked(self, e: ft.FilePickerResultEvent):
        if e.files:
            self._controller.get_metadata_excel_file(e.files)
        else:
            self.create_alert("No file selected!")

    def update_metadata_table(self, metadata_container: MetadataContainer):
        """Populate the metadata table with code, subdomain and value."""
        rows = []
        for code in sorted(metadata_container.get_cells().keys(), key=str.lower):
            metadata = metadata_container.get_metadata(code)
            if metadata is None:
                continue

            ontology = metadata.domain.ontology if metadata.domain else None
            ontology_value = ontology.value if ontology else ""
            synonyms = ", ".join(ontology.synonyms) if ontology and ontology.synonyms else ""
            iri = ontology.base_uri if ontology else ""

            rows.append(
                ft.DataRow(
                    cells=[
                        self._build_cell(metadata.code, "code"),
                        self._build_cell(metadata.subdomain, "subdomain"),
                        self._build_cell(metadata.cell_value, "value"),
                        self._build_cell(ontology_value, "ontology"),
                        self._build_cell(synonyms, "synonyms"),
                        self._build_cell(iri, "iri"),
                    ]
                )
            )

        self.dt_metadata.rows = rows
        self.update_page()

    @property
    def controller(self):
        return self._controller

    @controller.setter
    def controller(self, controller):
        self._controller = controller

    @property
    def page(self):
        return self._page

    def set_controller(self, controller):
        self._controller = controller

    def create_alert(self, message):
        dlg = ft.AlertDialog(title=ft.Text(message))
        self._page.open(dlg)
        self._page.update()

    def update_page(self):
        self._page.update()

    def _build_column(self, title: str, column_key: str) -> ft.DataColumn:
        width = self.COLUMN_WIDTHS.get(column_key)
        label_control: ft.Control = ft.Text(title)
        if width:
            label_control = ft.Container(width=width, content=ft.Text(title, weight=ft.FontWeight.BOLD))
        return ft.DataColumn(label_control)

    def _build_cell(self, value: str, column_key: str) -> ft.DataCell:
        width = self.COLUMN_WIDTHS.get(column_key)
        content = ft.Text(
            value or "",
            selectable=True,
            max_lines=None,
            overflow=ft.TextOverflow.VISIBLE,
        )
        if width:
            content = ft.Container(width=width, content=content)
        return ft.DataCell(content)