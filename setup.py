from setuptools import setup, find_packages

setup(
    name="student-ops-desk",
    version="0.1.1",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "chainlit>=1.0.0",
        "openai-agents>=0.0.1",
        "pydantic>=2.7.0",
        "python-dotenv>=1.0.0",
    ],
    python_requires=">=3.11",
    include_package_data=True,
    zip_safe=False,
)