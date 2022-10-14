from pathlib import Path

from setuptools import find_packages, setup


def read(fname):
    p = Path(__file__).parent / fname
    with p.open(encoding="utf-8") as f:
        return f.read()


setup(
    name="ocr_pipelines",
    version="0.0.1",
    author="Esukhia developers",
    author_email="esukhiadev@gmail.com",
    description="Ocr pipelines has importing bdrc work to opf and reimporting ocred opf",
    long_description=read("README.md"),
    long_description_content_type="text/markdown",
    license="Apache2",
    url="https://github.com/OpenPecha/OCR-Pipelines/",
    packages=find_packages(),
    install_requires=[
        "openpecha>=0.9.5, <1.0.0",
        "boto3>=1.24.50, <2.0",
        "Pillow>9.0.0, <=10.0.0",
        "Wand>=0.6.0, <=1.0.0",
        "google-cloud-vision>=3.1.4, <4.0.0"
    ],
    python_requires=">=3.8",
)
