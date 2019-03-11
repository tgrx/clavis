from pathlib import Path

from setuptools import find_packages, setup

here = Path(__file__).resolve().parent

with (here / "README.md").open("r", encoding="utf-8") as _readme_f:
    readme = _readme_f.read()

setup(
    name="clavis",
    version="0.0.1b3",
    description="Context manager for SQLAlchemy transaction",
    long_description=readme,
    long_description_content_type="text/markdown",
    url="https://gitlab.com/tgrx/clavis/",
    author="Alexander Sidorov",
    author_email="alex.n.sidorov@gmail.com",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Topic :: Database",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    keywords=" ".join(
        sorted({"contextlib", "db", "postgresql" "sqlalchemy", "sqlalchemy-core"})
    ),
    packages=find_packages(exclude=("build", "contrib", "dist", "docs", "tests")),
    install_requires=("SQLAlchemy>=1.1", "dynaconf>1"),
    python_requires=">=3.6",
)
