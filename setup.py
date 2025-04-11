from setuptools import setup

setup(
    name="code2xml",
    version="0.1.0",
    description="Convert code files to an XML structure with directory tree.",
    py_modules=["code2xml"],
    entry_points={
        "console_scripts": [
            "code2xml = code2xml:main",
        ],
    },
    python_requires=">=3.9",
)
