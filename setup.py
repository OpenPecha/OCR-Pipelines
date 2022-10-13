from pathlib import Path

from setuptools import find_packages, setup


def read(fname):
    p = Path(__file__).parent / fname
    with p.open(encoding="utf-8") as f:
        return f.read()


setup(
    name="ocr_pipelines",
    version="v.0.0.0",
    author="Esukhia developers",
    author_email="esukhiadev@gmail.com",
    description="Ocr pipelines has importing bdrc work to opf and reimporting ocred opf",
    long_description=read("README.md"),
    long_description_content_type="text/markdown",
    license="Apache2",
    url="https://github.com/OpenPecha/OCR-Pipelines/",
    packages=find_packages(),
    install_requires=[
        "openpecha>=0.9.0, <1.0.0",
        "Pillow>9.0.0, <=10.0.0"
    ],
    python_requires=">=3.7",
)