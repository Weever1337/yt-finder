import pathlib
from setuptools import setup

# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE / "README.md").read_text()

# This call to setup() does all the work
setup(
    name="yt-search",
    version="3.0.0",
    description="Perform YouTube video searches without the API. Fork of youtube-search",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/Weever1337/yt-search",
    author="Weever, Joe Tatusko",
    author_email="weever1337@gmail.com",
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    packages=["yt_search"],
    include_package_data=True,
    install_requires=["requests", "aiohttp"],
)
