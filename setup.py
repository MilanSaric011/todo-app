#!/usr/bin/env python3
from pathlib import Path
from setuptools import setup, find_packages

# Read README safely
readme_path = Path(__file__).parent / "README.md"
long_description = readme_path.read_text(encoding="utf-8") if readme_path.exists() else ""

setup(
    name="taskmaster",
    version="1.0.0",
    description="Professional TUI Task Manager with Zen-Dark theme",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Milan Saric",
    url="https://github.com/MilanSaric011/todo-app",
    python_requires=">=3.7",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Console :: Textual",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7+",
    ],
    py_modules=["taskmaster", "models", "constants"],
    scripts=["taskmaster.py"],
    entry_points={
        "console_scripts": [
            "taskmaster=taskmaster:main",
        ],
    },
    install_requires=[],
)
