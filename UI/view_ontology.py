import flet as ft


class ViewOntology(ft.Control):
    PRIMARY_COLOR = "#376966"
    PRIMARY_CONTAINER_COLOR = "#5A8F8A"
    SURFACE_COLOR = "#F7FAF9"
    SURFACE_VARIANT_COLOR = "#E0E7E6"
    OUTLINE_VARIANT_COLOR = "#C4D2D0"
    BUTTON_BG_COLOR = "#5C9792"
    BUTTON_TEXT_COLOR = "#FFFFFF"
    BUTTON_BG_COLOR_1 = "#6FAAA5"
    BUTTON_BG_COLOR_2 = "#5C9792"
    BUTTON_BG_COLOR_3 = "#4C8883"

    COLUMN_WIDTHS = {
        "code": 70,
        "domain": 120,
        "value": 140,
        "ontology": 120,
        "synonyms": 140,
        "iri": 180,
        "choice": 60,
    }

    def __init__(self, page: ft.Page):
        super().__init__()
        # page
        self._page = page
        self._page.title = "FoundingGIDE Ontology"
        self._page.horizontal_alignment = ft.CrossAxisAlignment.STRETCH
        self._page.scroll = ft.ScrollMode.AUTO

        # controller (it is not initialized. Must be initialized in the main,
        # after the controller is created)
        self._controller = None

        # graphical elements
        self.img_founding_gide = None
        self.btn_select_metadata_file = None
        self.btn_export_csv = None
        self.btn_reset_app = None
        self.file_picker = None
        self.directory_picker = None
        self.dd_export_format = None
        self.tbl_metadata = None
        self.btn_search = None
        self.chip_project_id = None
        self.chip_metadata_count = None
        self.empty_metadata_placeholder = None
        self.card_metadata_table = None
        self._dlg_reset = None
        self._dlg_export = None
        self._pending_export_format = "csv"
        self._choice_groups: dict[str, list[ft.Checkbox]] = {}
        self.search_progress = None
        self.search_status_text = None
        self.search_status_row = None

    def load_interface(self):
        """
        Initialize page theme, build controls, bind events, and mount the
        layout to the page.
        """
        self._configure_page()
        self._build_controls()
        self._set_initial_button_state()
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

    def update_metadata_table(
            self,
            metadata_rows: list[dict],
            project_id: str | None = None,
    ):
        """Populate the metadata table."""
        has_rows = bool(metadata_rows)
        self._choice_groups = {}
        self.tbl_metadata.rows = [
            ft.DataRow(
                color=self._row_color(row),
                cells=[
                    self._build_cell(row.get("code", ""), "code"),
                    self._build_cell(row.get("domain", ""), "domain"),
                    self._build_cell(row.get("value", ""), "value"),
                    self._build_cell(row.get("ontology", ""), "ontology"),
                    self._build_cell(row.get("synonyms", ""), "synonyms"),
                    self._build_cell(row.get("iri", ""), "iri"),
                    self._build_cell(row, "choice"),
                ]
            )

            for row in metadata_rows
        ]
        project_id_text = project_id or "—"
        self.chip_project_id.label = ft.Text(f"ID project: {project_id_text}")
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

    def _set_initial_button_state(self) -> None:
        if self.btn_search:
            self.btn_search.disabled = True
        if self.btn_export_csv:
            self.btn_export_csv.disabled = True
        if self.btn_select_metadata_file:
            self.btn_select_metadata_file.disabled = False
        if self.btn_reset_app:
            self.btn_reset_app.disabled = False

    def set_metadata_loaded_state(self) -> None:
        if self.btn_search:
            self.btn_search.disabled = False
        if self.btn_export_csv:
            self.btn_export_csv.disabled = True
        if self.btn_select_metadata_file:
            self.btn_select_metadata_file.disabled = False
        if self.btn_reset_app:
            self.btn_reset_app.disabled = False
        self.update_page()

    def set_after_search_state(self) -> None:
        if self.btn_select_metadata_file:
            self.btn_select_metadata_file.disabled = True
        if self.btn_export_csv:
            self.btn_export_csv.disabled = False
        if self.btn_reset_app:
            self.btn_reset_app.disabled = False
        self.update_page()

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
            bgcolor=self.BUTTON_BG_COLOR,
            color=self.BUTTON_TEXT_COLOR,
            expand=True
        )

        # button to export CSVs
        self.directory_picker = ft.FilePicker()
        self._page.overlay.append(self.directory_picker)
        self.dd_export_format = ft.Dropdown(
            label="Export format",
            value="csv",
            options=[
                ft.dropdown.Option("csv", "CSV (.csv)"),
                ft.dropdown.Option("excel", "Excel (.xlsx)"),
            ],
            width=220,
        )
        self.btn_export_csv = ft.FilledButton(
            text="Download",
            icon=ft.Icons.DOWNLOAD,
            tooltip="Download ontology exports in CSV or Excel format",
            bgcolor=self.BUTTON_BG_COLOR,
            color=self.BUTTON_TEXT_COLOR,
            expand=True
        )

        # button to reset the interface
        self.btn_reset_app = ft.FilledButton(
            text="Reset",
            icon=ft.Icons.RESTART_ALT,
            tooltip="Clear loaded data and reset the app",
            bgcolor=self.BUTTON_BG_COLOR,
            color=self.BUTTON_TEXT_COLOR,
            expand=True
        )
        # metadata table
        self.tbl_metadata = ft.DataTable(
            columns=[
                self._build_column("Code", "code"),
                self._build_column("Domain", "Domain"),
                self._build_column("Value", "value"),
                self._build_column("Ontology", "ontology"),
                self._build_column("Synonyms", "synonyms"),
                self._build_column("IRI", "iri"),
                self._build_column("", "choice"),
            ],
            rows=[],
            data_row_min_height=52,
            data_row_max_height=240,
            heading_row_color=self.SURFACE_VARIANT_COLOR,
            divider_thickness=0.8,
        )
        self.tbl_metadata.visible = False

        # button to search ontologies
        self.btn_search = ft.FilledTonalButton(
            text="Search ontologies",
            icon=ft.Icons.SEARCH,
            tooltip="Performs ontology searches on uploaded metadata",
            bgcolor=self.BUTTON_BG_COLOR,
            color=self.BUTTON_TEXT_COLOR,
        )

        # search progress indicator
        self.search_progress = ft.ProgressBar(
            width=180,
            value=None,
            color=self.PRIMARY_CONTAINER_COLOR,
        )
        self.search_status_text = ft.Text(
            "Searching ontologies...",
            size=12,
            color=self.PRIMARY_COLOR,
        )
        self.search_status_row = ft.Row(
            controls=[self.search_progress, self.search_status_text],
            spacing=12,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            visible=False,
        )

        # chip project id
        self.chip_project_id = ft.Chip(
            label=ft.Text("ID project: —"),
            leading=ft.Icon(ft.Icons.BADGE, size=18),
            bgcolor=self.PRIMARY_CONTAINER_COLOR,
            shape=ft.StadiumBorder(),
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
                    value="Load an Excel file to see the metadata organized "
                          "in the table.",
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
                expand=True,
                content=ft.Column(
                    controls=[
                        ft.Row(
                            controls=[
                                ft.Text(
                                    "Metadata", size=18,
                                    weight=ft.FontWeight.W_600
                                ),
                                self.chip_project_id,
                                self.chip_metadata_count,
                                ft.Container(expand=True),
                                self.btn_search,
                            ],
                            vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        ),
                        ft.Divider(height=12, thickness=1,
                                   color=self.OUTLINE_VARIANT_COLOR),
                        self.search_status_row,
                        ft.Container(
                            bgcolor=self.SURFACE_COLOR,
                            border_radius=12,
                            padding=8,
                            content=ft.Column(
                                controls=[
                                    ft.Row(
                                        [ft.Container(
                                            expand=True,
                                            content=self.tbl_metadata
                                        )],
                                        scroll=ft.ScrollMode.AUTO,
                                        expand=True,
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
            controls=[
                self.img_founding_gide,
                ft.Row(
                    controls=[
                        self.btn_select_metadata_file,
                        self.btn_export_csv,
                        self.btn_reset_app,
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    spacing=12,
                ),
                ft.Row(
                    controls=[ft.Container(content=self.card_metadata_table)],
                    alignment=ft.MainAxisAlignment.CENTER,
                    expand=True,
                ),
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
        self.directory_picker.on_result = self.on_directory_picked
        self.btn_export_csv.on_click = self.show_export_dialog
        self.btn_reset_app.on_click = self._controller.request_reset

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

    def show_reset_confirmation(self, on_confirm) -> None:
        """Open a confirmation dialog before resetting the application."""
        if self._dlg_reset:
            self._page.close(self._dlg_reset)

        def on_cancel(_):
            self._page.close(self._dlg_reset)

        def on_accept(_):
            self._page.close(self._dlg_reset)
            on_confirm()

        self._dlg_reset = ft.AlertDialog(
            modal=True,
            title=ft.Text("Reset the application?"),
            content=ft.Text(
                "This will clear loaded metadata, selections, and results."
            ),
            actions=[
                ft.TextButton("Cancel", on_click=on_cancel),
                ft.FilledButton(
                    "Reset",
                    icon=ft.Icons.RESTART_ALT,
                    on_click=on_accept,
                ),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        self._page.open(self._dlg_reset)

    def reset_interface(self) -> None:
        """Restore the interface to its initial empty state."""
        self.tbl_metadata.rows = []
        self.tbl_metadata.visible = False
        self.empty_metadata_placeholder.visible = True
        self.chip_project_id.label = ft.Text("ID project: —")
        self.chip_metadata_count.label = ft.Text("0 elements")
        if self.search_status_row:
            self.search_status_row.visible = False
        self._set_initial_button_state()
        self._choice_groups = {}
        self.update_page()

    def show_export_dialog(self, _) -> None:
        """Prompt the user for export format before choosing a folder."""
        if self._dlg_export:
            self._page.close(self._dlg_export)

        def on_cancel(_):
            self._page.close(self._dlg_export)

        def on_confirm(_):
            selected_format = (
                self.dd_export_format.value
                if self.dd_export_format
                else "csv"
            )
            self._pending_export_format = selected_format or "csv"
            self._page.close(self._dlg_export)
            self.directory_picker.get_directory_path()

        self._dlg_export = ft.AlertDialog(
            modal=True,
            title=ft.Text("Download ontology exports"),
            content=ft.Column(
                [
                    ft.Text("Choose the format to download."),
                    self.dd_export_format,
                ],
                tight=True,
            ),
            actions=[
                ft.TextButton("Cancel", on_click=on_cancel),
                ft.FilledButton(
                    "Download",
                    icon=ft.Icons.DOWNLOAD,
                    on_click=on_confirm,
                ),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        self._page.open(self._dlg_export)

    def set_search_loading(self, is_loading: bool) -> None:
        """Toggle the search progress indicator and search button state."""
        if self.search_status_row:
            self.search_status_row.visible = is_loading
        if self.btn_search:
            self.btn_search.disabled = is_loading
        self.update_page()

    def on_directory_picked(self, e: ft.FilePickerResultEvent):
        """Handle directory selection for exports."""
        if e.path:
            export_format = self._pending_export_format or "csv"
            self._controller.export_csv(e.path, export_format)
        else:
            self.create_alert("No folder selected!")

    def _build_column(self, title: str, column_key: str) -> ft.DataColumn:
        """ Return a configured DataColumn for the metadata table."""
        width = self.COLUMN_WIDTHS.get(column_key)
        label_control: ft.Control = ft.Text(title)
        if width:
            label_text = ft.Text(
                title,
                weight=ft.FontWeight.BOLD,
            )
            label_control = ft.Container(
                width=width,
                content=label_text,
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
                controls=[icon_button],
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
        alignment = (
            ft.alignment.center
            if column_key == "choice"
            else ft.alignment.center_left
        )
        content = ft.Container(
            width=width,
            content=content,
            alignment=alignment,
            expand=True,
        )
        return ft.DataCell(content)

    def _build_choice_cell(self, row: dict) -> ft.Control:
        option = row.get("selection_option")
        if not option:
            return ft.Text("")
        selected_value = row.get("selected_value") or None

        group_id = row.get("selection_group")
        checkbox = ft.Checkbox(
            value=option["value"] == selected_value,
            label="",
            data=option["value"],
        )

        if group_id:
            self._choice_groups.setdefault(group_id, []).append(checkbox)

            def on_change(e, group=group_id):
                if not e.control.value:
                    group_checkboxes = self._choice_groups.get(group, [])
                    if group_checkboxes:
                        default_checkbox = group_checkboxes[0]
                        for group_checkbox in group_checkboxes:
                            group_checkbox.value = (group_checkbox is
                                                    default_checkbox)
                        self._controller.set_user_selection(
                            group, default_checkbox.data
                        )
                        for group_checkbox in group_checkboxes:
                            group_checkbox.update()
                    return

                for group_checkbox in self._choice_groups.get(group, []):
                    group_checkbox.value = group_checkbox is e.control
                self._controller.set_user_selection(group, e.control.data)
                for group_checkbox in self._choice_groups.get(group, []):
                    group_checkbox.update()

            checkbox.on_change = on_change

        return checkbox

    def _row_color(self, row: dict) -> str:
        group_index = row.get("group_index")
        if group_index is None:
            return ""
        return self.SURFACE_COLOR if group_index % 2 == 0 \
            else self.SURFACE_VARIANT_COLOR