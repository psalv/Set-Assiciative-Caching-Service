import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="n_way_set_associative_cache",
    version="1.0.0",
    author="Paul Salvatore",
    author_email="paulanthonysalvatore@gmail.com",
    description="An N-Way Set Associative Cache",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=setuptools.find_packages(),
    classifiers=(
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ),
)