<a href="https://founding-gide.eurobioimaging.eu/">
  <img src="assets/images/foundingGIDE.png" alt="FoundingGIDE logo" width="220">
</a>
# FoundingGIDE Ontology

A desktop application for mapping metadata fields from a structured Excel template to ontology terms using the BioPortal search API. The UI is built with Flet, and the backend loads metadata mappings from JSON, queries BioPortal for candidate terms, and exports curated ontology selections to CSV or Excel.

## Key Features

- **Template-driven metadata ingestion**: reads specific cells from a predefined Excel worksheet and validates labels before extraction.
- **Ontology lookup workflow**: queries BioPortal per metadata term and displays selectable candidate terms.
- **Domain-to-ontology mapping**: drives ontology selection based on domain metadata from JSON configuration.
- **Export pipeline**: produces ontology codes and synonym lists as CSV or Excel files.

## Architecture Overview

| Layer | Responsibilities | Key Modules |
| --- | --- | --- |
| UI | Flet-based desktop interface, search and export workflow | `UI/view_ontology.py`, `UI/controller_ontology.py` |
| Model | Domain logic, ontology search, export orchestration | `model/model_ontology.py`, `model/bio_portal_client.py` |
| Persistence | Domain and metadata mappings | `persistence/domain_ontology.json`, `persistence/metadata_mapping.json` |
| Services | Excel read/write utilities | `services/metadata_file_io.py` |

## Requirements

- Python 3.10+ (recommended)
- BioPortal API key
- Dependencies listed in `requirements.txt`

## Setup

1. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Create a `.env` file**
   - The app expects a `.env` file at `config/.env`.
   - Add your BioPortal API key:
     ```bash
     BIOPORTAL_API_KEY=your_bioportal_api_key
     ```

3. **Run the application**
   ```bash
   python main.py
   ```

## Metadata Template Expectations

The application reads a specific worksheet and column in your Excel file based on `persistence/metadata_mapping.json`:

- **Sheet name**: `metadata template`
- **Value column index**: `4` (column D)
- **Cell labels**: The label text in the template must match the `cell_name` values in the mapping file.
- **Dataset ID**: The cell for domain `dataset` is used as the dataset identifier and is required for exported file naming.

If the sheet name or label text does not match, the app will skip those cells and continue processing.

## Domain-to-Ontology Mapping

`persistence/domain_ontology.json` defines which BioPortal ontology is used for each domain (e.g., `disease → DOID`, `drugs → CHEBI`). This mapping controls the ontology queried for each metadata field.

## Workflow

1. **Select Excel file**: load the metadata template populated with user values.
2. **Search ontology terms**: the app queries BioPortal and shows the top matches.
3. **Select preferred term**: choose the correct ontology code from the candidates.
4. **Export results**:
   - `ontology_export.csv` / `ontology_export.xlsx`
   - `ontology_export_synonyms.csv` / `ontology_export_synonyms.xlsx`

## Export Outputs

The export creates up to two files:

- **Ontology codes**: one row per dataset, with ontology codes grouped by domain.
- **Ontology synonyms**: a two-column list of `OntologyCode` and `Synonyms` for selections.

Export format can be CSV or Excel, and filenames are prefixed with the dataset ID when available.

## Development Notes

- The UI workflow is event-driven and uses Flet’s `Page` APIs.
- BioPortal responses are normalized to derive compact codes and canonical PURLs where possible.
- Metadata values can contain multiple comma-separated terms; each term is searched independently.

## Troubleshooting

- **Missing API key**: ensure `config/.env` exists and contains `BIOPORTAL_API_KEY`.
- **No results**: confirm internet access and verify that the target ontology contains your term.
- **Template mismatch**: ensure sheet name and label text align with `metadata_mapping.json`.