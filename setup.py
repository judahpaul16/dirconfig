from setuptools import setup, find_packages

setup(
    name="dirconfig",
    version="0.2.2",
    author="Judah Paul",
    author_email="me@judahpaul.com",
    description="A simple directory configuration tool",
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",
    url="https://github.com/judahpaul16/dirconfig",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    entry_points={
        "console_scripts": [
            "dirconfig=dirconfig.main:main",
        ],
    },
    install_requires=[
        "PyYAML==6.0.1",
        "watchdog==4.0.0"
    ],
)
