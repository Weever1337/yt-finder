import pathlib
from setuptools import setup

# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE / "README.md").read_text()

# This call to setup() does all the work
setup(
    name="yt-finder",
    version="1.1.0",
    description="Perform YouTube video searches without the API. Fork of the youtube-search library.",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/Weever1337/yt-finder",
    author="NixxO (nixxoq), Weever (weever1337), Joe Tatusko (original author)",
    author_email="weever1337@gmail.com",
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    packages=["yt_finder"],
    include_package_data=True,
    install_requires=["loguru", "aiohttp"],
)
