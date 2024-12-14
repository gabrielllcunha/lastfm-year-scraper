from setuptools import setup, find_packages

setup(
    name="lastfm_year_scrapper",
    version="1.0.0",
    description="Python scripts to scrape Last.fm data",
    author="Gabriel Cunha",
    packages=find_packages(),
    install_requires=[
        "playwright",
        "flask",
    ],
)
