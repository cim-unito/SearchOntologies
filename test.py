import flet as ft

DATA = [
    {
        "keyword": "Cancer",
        "field": "Disease",
        "ontology": "DOID:1234",
        "label": "Malattia",
        "synonyms": ["Neoplasia", "Tumor"],
        "doi": ["10.1234/abc", "10.5678/xyz"],
        "bioportal_results": ["NCIT:C9305", "MONDO:0004992"]
    },
    {
        "keyword": "BRCA1",
        "field": "Mutation",
        "ontology": "HGNC:1100",
        "label": "Gene",
        "synonyms": ["Breast cancer 1"],
        "doi": ["10.1111/brca"],
        "bioportal_results": ["SO:0000704"]
    }
]

def main(page: ft.Page):
    page.title = "BioPortal – Table View"
    page.padding = 20
    page.scroll = ft.ScrollMode.AUTO

    detail_panel = ft.Container(
        padding=15,
        border_radius=10,
        bgcolor=ft.Colors.GREY_100,
        visible=False
    )

    def show_details(item):
        detail_panel.content = ft.Column([
            ft.Text(f"Keyword: {item['keyword']}", weight="bold", size=18),
            ft.Text(f"Ontologia: {item['ontology']}"),
            ft.Divider(),
            ft.Text("Sinonimi", weight="bold"),
            ft.Column([ft.Text(s) for s in item["synonyms"]]),
            ft.Divider(),
            ft.Text("DOI trovati", weight="bold"),
            ft.Column([ft.Text(d) for d in item["doi"]]),
            ft.Divider(),
            ft.Text("Altri risultati BioPortal", weight="bold"),
            ft.Column([ft.Text(r) for r in item["bioportal_results"]]),
        ])
        detail_panel.visible = True
        page.update()

    rows = []
    for item in DATA:
        rows.append(
            ft.DataRow(
                cells=[
                    ft.DataCell(ft.Text(item["keyword"])),
                    ft.DataCell(ft.Text(item["field"])),
                    ft.DataCell(ft.Text(item["ontology"])),
                    ft.DataCell(
                        ft.IconButton(
                            icon=ft.Icons.OPEN_IN_NEW,
                            tooltip="Mostra dettagli",
                            on_click=lambda e, i=item: show_details(i)
                        )
                    ),
                ]
            )
        )

    table = ft.DataTable(
        columns=[
            ft.DataColumn(ft.Text("Keyword")),
            ft.DataColumn(ft.Text("Campo")),
            ft.DataColumn(ft.Text("Ontologia")),
            ft.DataColumn(ft.Text("Dettagli")),
        ],
        rows=rows,
    )

    page.add(
        ft.Text("Risultati BioPortal", size=22, weight="bold"),
        table,
        detail_panel,
    )

ft.app(target=main)
