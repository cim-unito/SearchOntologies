import flet as ft

from model.model_ontology import ModelOntology
from UI.view_ontology import ViewOntology
from UI.controller_ontology import ControllerOntology


def main(page: ft.Page):
    ontology_model = ModelOntology()
    ontology_view = ViewOntology(page)
    ontology_controller = ControllerOntology(ontology_view, ontology_model)
    ontology_view.set_controller(ontology_controller)
    ontology_view.load_interface()


if __name__ == "__main__":
    ft.app(target=main)

