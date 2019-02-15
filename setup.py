from setuptools import find_packages, setup

setup(
    name="clavis",
    version="0.0.1b3",
    description="Context manager for SQLAlchemy transaction",
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
