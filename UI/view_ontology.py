import flet as ft


class ViewOntology(ft.Control):
    COLUMN_WIDTHS = {
        "code": 100,
        "subdomain": 140,
        "value": 180,
        "ontology": 140,
        "synonyms": 200,
        "iri": 320,
    }

    def __init__(self, page: ft.Page):
        super().__init__()
        # page
        self._page = page
        self._page.title = "FoundingGIDE Ontology"
        self._page.horizontal_alignment = "CENTER"
        self._page.scroll = ft.ScrollMode.AUTO

        # controller (it is not initialized. Must be initialized in the main,
        # after the controller is created)
        self._controller = None

        # graphical elements
        self._img_founding_gide = None
        self.btn_select_file = None
        self.file_picker = None
        self.dt_metadata = None
        self.btn_search = None
        self.chip_records = None
        self.empty_state = None

    def load_interface(self):
        self._configure_page()

        # logo founding gide
        self._img_founding_gide = ft.Column(
            [
                ft.Image(src="assets/images/foundingGIDE.png", width=260,
                         fit=ft.ImageFit.CONTAIN),
            ],
            spacing=4,
        )

        # button select the metadata excel file
        self.file_picker = ft.FilePicker(on_result=self.on_file_picked)
        self._page.overlay.append(self.file_picker)
        self.btn_select_file = ft.FilledButton(
            text="Select Excel metadata file",
            icon=ft.Icons.UPLOAD_FILE,
            on_click=lambda _: self.file_picker.pick_files(
                allow_multiple=False,
                allowed_extensions=["xlsx"],
            ),
        )

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
            data_row_min_height=52,
            data_row_max_height=240,
            heading_row_color=ft.Colors.ON_SURFACE_VARIANT,
            divider_thickness=0.8,
        )
        self.dt_metadata.visible = False

        table_width = sum(self.COLUMN_WIDTHS.values()) + 80

        # button to search ontologies
        self.btn_search = ft.FilledTonalButton(
            text="Search ontologies",
            icon=ft.Icons.SEARCH,
            on_click=self._controller.lookup_term,
            tooltip="Performs ontology searches on uploaded metadata",
        )

        # chip records
        self.chip_records = ft.Chip(
            label=ft.Text("0 elementi"),
            leading=ft.Icon(ft.Icons.TABLE_ROWS, size=18),
            bgcolor=ft.Colors.PRIMARY_CONTAINER,
            shape=ft.StadiumBorder(),
        )

        # empty state
        self.empty_state = ft.Column(
            [
                ft.Icon(ft.Icons.TABLE_VIEW, size=56, color=ft.Colors.PRIMARY),
                ft.Text(
                    "Load an Excel file to see the metadata organized in the table.",
                    text_align=ft.TextAlign.CENTER,
                ),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            visible=True,
        )

        table_card = ft.Card(
            elevation=2,
            content=ft.Container(
                padding=16,
                width=table_width,
                content=ft.Column(
                    [
                        ft.Row(
                            [
                                ft.Text(
                                    "Metadata", size=18,
                                    weight=ft.FontWeight.W_600
                                ),
                                self.chip_records,
                                ft.Container(expand=True),
                                self.btn_search,
                            ],
                            vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        ),
                        ft.Divider(height=12, thickness=1,
                                   color=ft.Colors.OUTLINE_VARIANT),
                        ft.Container(
                            bgcolor=ft.Colors.SURFACE,
                            border_radius=12,
                            padding=8,
                            content=ft.Column(
                                [
                                    self.dt_metadata,
                                    self.empty_state,
                                ],
                                scroll=ft.ScrollMode.AUTO,
                                expand=True,
                            ),
                        ),
                    ],
                    spacing=12,
                ),
            ),
        )

        controls_layout = ft.Column(
            [
                self._img_founding_gide,
                ft.Row(
                    [
                        self.btn_select_file,
                    ],
                    spacing=16,
                    alignment=ft.MainAxisAlignment.START,
                ),
                table_card,
            ],
            spacing=20,
            width=table_width,
        )

        self._page.controls.append(
            ft.Container(
                padding=20,
                expand=True,
                content=ft.Column(
                    [controls_layout],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                ),
            )
        )

        self._page.update()

    def _configure_page(self):
        self._page.theme_mode = ft.ThemeMode.LIGHT
        self._page.padding = 20
        self._page.bgcolor = ft.Colors.SURFACE_TINT
        self._page.theme = ft.Theme(
            color_scheme_seed=ft.Colors.BLUE,
            use_material3=True,
        )
        self._page.appbar = ft.AppBar(
            title=ft.Text("FoundingGIDE Ontology"),
            center_title=False,
            bgcolor=ft.Colors.SURFACE,
            actions=[
                ft.IconButton(
                    icon=ft.Icons.HELP_OUTLINE,
                    tooltip="Select an Excel file and start the search",
                )
            ],
        )

    def on_file_picked(self, e: ft.FilePickerResultEvent):
        if e.files:
            self.empty_state.visible = False
            self.dt_metadata.visible = True
            self._controller.get_metadata_excel_file(e.files)
        else:
            self.create_alert("No file selected!")

    def update_metadata_table(self, metadata_rows: list[dict]):
        """Populate the metadata table with pre-serialized rows."""
        has_rows = bool(metadata_rows)
        self.dt_metadata.rows = [
            ft.DataRow(
                cells=[
                    self._build_cell(row.get("code", ""), "code"),
                    self._build_cell(row.get("subdomain", ""), "subdomain"),
                    self._build_cell(row.get("value", ""), "value"),
                    self._build_cell(row.get("ontology", ""), "ontology"),
                    self._build_cell(row.get("synonyms", ""), "synonyms"),
                    self._build_cell(row.get("iri", ""), "iri"),
                ]
            )

            for row in metadata_rows
        ]
        self.chip_records.label = ft.Text(f"{len(metadata_rows)} elementi")
        self.dt_metadata.visible = has_rows
        self.empty_state.visible = not has_rows
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
            label_control = ft.Container(
                width=width,
                content=ft.Text(title, weight=ft.FontWeight.BOLD),
            )
        return ft.DataColumn(label_control)

    def _build_cell(self, value: str, column_key: str) -> ft.DataCell:
        width = self.COLUMN_WIDTHS.get(column_key)

        if column_key == "iri" and value:
            icon_button = ft.IconButton(
                icon=ft.Icons.OPEN_IN_NEW,
                on_click=lambda _, url=value: self._page.launch_url(url),
                tooltip=value,
                icon_color=ft.Colors.BLUE,
                style=ft.ButtonStyle(
                    padding=0,
                    overlay_color=ft.Colors.TRANSPARENT,
                ),
            )
            content = ft.Row(
                [icon_button],
                spacing=8,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            )
        else:
            content = ft.Text(
                value or "",
                selectable=True,
                max_lines=3,
                overflow=ft.TextOverflow.ELLIPSIS,
            )
        if width:
            content = ft.Container(width=width, content=content)
        return ft.DataCell(content)
