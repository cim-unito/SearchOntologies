import flet as ft

from model.model import Model
from UI.view import View
from UI.controller import Controller


def main(page: ft.Page):
    ontology_model = Model()
    ontology_view = View(page)
    ontology_controller = Controller(ontology_view, ontology_model)
    ontology_view.set_controller(ontology_controller)
    ontology_view.load_interface()


ft.app(target=main)
