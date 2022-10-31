
# OCR-Pipelines

[![CI](https://github.com/OpenPecha/OCR-Pipelines/actions/workflows/CI.yaml/badge.svg)](https://github.com/OpenPecha/OCR-Pipelines/actions/workflows/CI.yaml)

Ocr pipelines has importing bdrc work to opf and reimporting ocred opf

## Developer Installation.

#### `pip install git+https://github.com/OpenPecha/OCR-Pipelines`

```bash
git clone https://github.com/OpenPecha/OCR-Pipelines.git
cd OCR-Pipelines
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
pip install -e .
```

### `!Important: Please setup pre-commit`

```bash
pre-commit install
```

## Testing
```bash
pytest tests
```
