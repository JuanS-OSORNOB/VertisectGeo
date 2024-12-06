from setuptools import setup, find_packages

setup(
    name="VertisectGeo",
    version="0.1",
    packages=find_packages(),
    package_dir={'':'src'},
    install_requires = ['requests==2.31.0'],
    entry_points={'console_scripts':['VertisectGeo=src.main:main']}
)
