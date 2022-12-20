import re
from pathlib import Path

from setuptools import find_packages, setup


def read(fname):
    p = Path(__file__).parent / fname
    with p.open(encoding="utf-8") as f:
        return f.read()


def get_version(prop, project):
    project = Path(__file__).parent / project / "__init__.py"
    result = re.search(rf'{prop}\s*=\s*[\'"]([^\'"]*)[\'"]', project.read_text())
    if result is None:
        raise Exception(f"Unable to find version string for {prop} in {project}")
    return result.group(1)


setup(
    name="ocr_pipelines",
    version=get_version("__version__", "ocr_pipelines"),
    author="Esukhia developers",
    author_email="esukhiadev@gmail.com",
    description="Ocr pipelines has importing bdrc work to opf and reimporting ocred opf",
    long_description=read("README.md"),
    long_description_content_type="text/markdown",
    license="Apache2",
    url="https://github.com/OpenPecha/OCR-Pipelines/",
    packages=find_packages(),
    install_requires=[
        "openpecha>=0.9.17, <1.0.0",
        "boto3>=1.24.50, <2.0",
        "Pillow>9.0.0, <=10.0.0",
        "Wand>=0.6.0, <=1.0.0",
        "google-cloud-vision>=3.1.4, <4.0.0",
    ],
    python_requires=">=3.8",
)
