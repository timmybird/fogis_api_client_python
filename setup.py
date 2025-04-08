import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="fogis-api-client-timmyBird",
    version="0.0.8",
    author="Bartek Svaberg",
    author_email="bartek.svaberg@gmail.com",
    description="A Python client for the FOGIS API (Svensk Fotboll)",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/timmyBird/fogis-api-client",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.7',
    install_requires=[
        "requests",
        "beautifulsoup4",
        "flask",
        "apispec>=6.0.0",
        "flask-swagger-ui",
        "marshmallow",
    ],
    extras_require={
        'dev': [
            'pytest',
            'pytest-mock',
            'pytest-cov',
            'flake8',
            'docker',
            'apispec>=6.0.0',
            'flask-swagger-ui',
            'marshmallow',
        ],
    },
    include_package_data=True,
)
