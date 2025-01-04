"""setup.py for the Zinny API package."""
from setuptools import setup, find_packages

setup(
    name="zinny-api",
    version="1.0.0",
    packages=find_packages(where="src"),
    package_dir={"zinny_api": "src/zinny_api"},
    include_package_data=True,
    entry_points={
        "console_scripts": [
            "zinny-api=main:main",
        ]
    },
    install_requires=[
        "flask",
        "zinny-surveys @ git+https://github.com/RyLaney/zinny-surveys.git#egg=zinny-surveys",
    ],
    extras_require={
        "dev": [
            "setuptools",
            "wheel",
            "pytest",
            "black",
        ]
    },
    description="Zinny is an app designed to evaluate titles using surveys. This is the APU for the Zinny app.",
    author="Ryan Laney",
    url="https://github.com/RyLaney/zinny-api",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.11",
    license='BSD License',

)
