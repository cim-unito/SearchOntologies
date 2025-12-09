import flet as ft


class ViewOntology(ft.Control):
    def __init__(self, page: ft.Page):
        super().__init__()
        # page
        self._page = page
        self._page.title = "FoundingGIDE Ontology "
        self._page.horizontal_alignment = 'CENTER'
        self._page.theme_mode = ft.ThemeMode.DARK
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
                ft.DataColumn(ft.Text("Keyword")),
                ft.DataColumn(ft.Text("Value")),
                ft.DataColumn(ft.Text("Ontology")),
                ft.DataColumn(ft.Text("Synonyms")),
                ft.DataColumn(ft.Text("IRI")),
            ],
            rows=[],
        )
        self._page.controls.append(self.dt_metadata)

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

    def display_metadata(self, file_path: str, metadata: dict[str, object]):
        lines = [f"File: {file_path}"]
        for key, value in metadata.items():
            lines.append(f"{key}: {value}")
        self.metadata_display.value = "\n".join(lines)
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
