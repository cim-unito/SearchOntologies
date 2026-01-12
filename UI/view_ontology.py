import flet as ft


class ViewOntology(ft.Control):
    PRIMARY_COLOR = "#376966"
    PRIMARY_CONTAINER_COLOR = "#5A8F8A"
    SURFACE_COLOR = "#F7FAF9"
    SURFACE_VARIANT_COLOR = "#E0E7E6"
    OUTLINE_VARIANT_COLOR = "#C4D2D0"

    COLUMN_WIDTHS = {
        "code": 90,
        "subdomain": 120,
        "value": 160,
        "ontology": 150,
        "synonyms": 180,
        "iri": 240,
        "choice": 180,
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
        self.img_founding_gide = None
        self.btn_select_metadata_file = None
        self.file_picker = None
        self.tbl_metadata = None
        self.btn_search = None
        self.chip_metadata_count = None
        self.empty_metadata_placeholder = None
        self.card_metadata_table = None

    def load_interface(self):
        """
        Initialize page theme, build controls, bind events, and mount the
        layout to the page.
        """
        self._configure_page()
        self._build_controls()
        self._bind_events()
        controls_layout = self._define_layout()

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

    def update_metadata_table(self, metadata_rows: list[dict]):
        """Populate the metadata table."""
        has_rows = bool(metadata_rows)
        self.tbl_metadata.rows = [
            ft.DataRow(
                color=self._row_color(row),
                cells=[
                    self._build_cell(row.get("code", ""), "code"),
                    self._build_cell(row.get("subdomain", ""), "subdomain"),
                    self._build_cell(row.get("value", ""), "value"),
                    self._build_cell(row.get("ontology", ""), "ontology"),
                    self._build_cell(row.get("synonyms", ""), "synonyms"),
                    self._build_cell(row.get("iri", ""), "iri"),
                    self._build_cell(row, "choice"),
                ]
            )

            for row in metadata_rows
        ]
        self.chip_metadata_count.label = ft.Text(
            f"{len(metadata_rows)} elements")
        self.tbl_metadata.visible = has_rows
        self.empty_metadata_placeholder.visible = not has_rows
        self.update_page()

    def create_alert(self, message):
        dlg = ft.AlertDialog(title=ft.Text(message))
        self._page.open(dlg)
        self._page.update()

    def update_page(self):
        self._page.update()

    def set_controller(self, controller):
        self._controller = controller

    @property
    def controller(self):
        return self._controller

    @controller.setter
    def controller(self, controller):
        self._controller = controller

    @property
    def page(self):
        return self._page

    def _configure_page(self):
        self._page.theme_mode = ft.ThemeMode.LIGHT
        self._page.padding = 20
        self._page.bgcolor = self.PRIMARY_COLOR
        self._page.theme = ft.Theme(
            color_scheme_seed=self.PRIMARY_COLOR,
            use_material3=True,
        )
        self._page.appbar = ft.AppBar(
            title=ft.Text("FoundingGIDE Ontology"),
            center_title=False,
            bgcolor=self.SURFACE_COLOR,
            actions=[
                ft.IconButton(
                    icon=ft.Icons.HELP_OUTLINE,
                    tooltip="Select an Excel file and start the search",
                )
            ],
        )

    def _build_controls(self):
        # logo founding gide
        self.img_founding_gide = ft.Column(
            [
                ft.Image(src="assets/images/foundingGIDE.png", width=260,
                         fit=ft.ImageFit.CONTAIN),
            ],
            spacing=4,
        )

        # button select the metadata excel file
        self.file_picker = ft.FilePicker()
        self._page.overlay.append(self.file_picker)
        self.btn_select_metadata_file = ft.FilledButton(
            text="Select metadata file",
            icon=ft.Icons.UPLOAD_FILE,
            tooltip="Select the metadata excel file to search for ontologies",
        )

        # metadata table
        self.tbl_metadata = ft.DataTable(
            columns=[
                self._build_column("Code", "code"),
                self._build_column("Subdomain", "subdomain"),
                self._build_column("Value", "value"),
                self._build_column("Ontology", "ontology"),
                self._build_column("Synonyms", "synonyms"),
                self._build_column("IRI", "iri"),
                self._build_column("Choice", "choice"),
            ],
            rows=[],
            data_row_min_height=52,
            data_row_max_height=240,
            heading_row_color=self.SURFACE_VARIANT_COLOR,
            divider_thickness=0.8,
        )
        self.tbl_metadata.visible = False

        table_width = sum(self.COLUMN_WIDTHS.values()) + 80

        # button to search ontologies
        self.btn_search = ft.FilledTonalButton(
            text="Search ontologies",
            icon=ft.Icons.SEARCH,
            tooltip="Performs ontology searches on uploaded metadata",
        )

        # chip records
        self.chip_metadata_count = ft.Chip(
            label=ft.Text("0 elements"),
            leading=ft.Icon(ft.Icons.TABLE_ROWS, size=18),
            bgcolor=self.PRIMARY_CONTAINER_COLOR,
            shape=ft.StadiumBorder(),
        )

        # empty table state
        self.empty_metadata_placeholder = ft.Column(
            [
                ft.Icon(ft.Icons.TABLE_VIEW, size=56,
                        color=self.PRIMARY_COLOR),
                ft.Text(
                    "Load an Excel file to see the metadata organized in the table.",
                    text_align=ft.TextAlign.CENTER,
                ),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            visible=True,
        )

        # card for the table
        self.card_metadata_table = ft.Card(
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
                                self.chip_metadata_count,
                                ft.Container(expand=True),
                                self.btn_search,
                            ],
                            vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        ),
                        ft.Divider(height=12, thickness=1,
                                   color=self.OUTLINE_VARIANT_COLOR),
                        ft.Container(
                            bgcolor=self.SURFACE_COLOR,
                            border_radius=12,
                            padding=8,
                            content=ft.Column(
                                [
                                    ft.Row(
                                        [self.tbl_metadata],
                                        scroll=ft.ScrollMode.AUTO,
                                    ),
                                    self.empty_metadata_placeholder,
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

    def _define_layout(self) -> ft.Column:
        controls_layout = ft.Column(
            [
                self.img_founding_gide,
                self.btn_select_metadata_file,
                self.card_metadata_table,
            ],
            spacing=20,
        )

        return controls_layout

    def _bind_events(self):
        """
        Wire UI events to controller callbacks; requires controller to be set.
        """
        self.file_picker.on_result = self.on_file_picked
        self.btn_select_metadata_file.on_click = lambda \
                _: self.file_picker.pick_files(
            allow_multiple=False,
            allowed_extensions=["xlsx"],
        )
        self.btn_search.on_click = self._controller.lookup_term

    def on_file_picked(self, e: ft.FilePickerResultEvent):
        """
        Handle file picker result, showing the table and delegating file
        processing to the controller; alert when no file is selected.
        """
        if e.files:
            self.empty_metadata_placeholder.visible = False
            self.tbl_metadata.visible = True
            self._controller.get_metadata_excel_file(e.files)
        else:
            self.create_alert("No file selected!")

    def _build_column(self, title: str, column_key: str) -> ft.DataColumn:
        """ Return a configured DataColumn for the metadata table."""
        width = self.COLUMN_WIDTHS.get(column_key)
        label_control: ft.Control = ft.Text(title)
        if width:
            label_control = ft.Container(
                width=width,
                content=ft.Text(title, weight=ft.FontWeight.BOLD),
            )
        return ft.DataColumn(label_control)

    def _build_cell(self, value, column_key: str) -> ft.DataCell:
        """
        Return a configured DataCell for the metadata table, applying width
         and content formatting (IRI links open externally).
        """
        width = self.COLUMN_WIDTHS.get(column_key)

        if column_key == "choice":
            content = self._build_choice_cell(value)
        elif column_key == "iri" and value:
            icon_button = ft.IconButton(
                icon=ft.Icons.OPEN_IN_NEW,
                on_click=lambda _, url=value: self._page.launch_url(url),
                tooltip=value,
                icon_color=self.PRIMARY_COLOR,
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

    def _build_choice_cell(self, row: dict) -> ft.Control:
        options = row.get("selection_options") or []
        if not options:
            return ft.Text("")
        if len(options) == 1:
            option = options[0]
            return ft.Text(option.get("label") or option.get("value") or "")

        selected_value = row.get("selected_value") or None
        checkboxes: list[ft.Checkbox] = []

        def on_change(e, group=row.get("selection_group")):
            if not e.control.value:
                self._controller.set_user_selection(group, "")
                return

            for checkbox in checkboxes:
                checkbox.value = checkbox is e.control
            self._controller.set_user_selection(group, e.control.data)
            for checkbox in checkboxes:
                checkbox.update()

        for option in options:
            checkbox = ft.Checkbox(
                value=option["value"] == selected_value,
                label=option["label"],
                data=option["value"],
                on_change=on_change,
            )
            checkboxes.append(checkbox)

        return ft.Column(checkboxes, spacing=0)
    def _row_color(self, row: dict) -> str:
        group_index = row.get("group_index")
        if group_index is None:
            return ""
        return self.SURFACE_COLOR if group_index % 2 == 0 \
            else self.SURFACE_VARIANT_COLOR