from setuptools import setup

setup(
    name='musicphreak',
    packages=['musicphreak'],
    include_package_data=True,
    install_requires=[
        'flask',
        'beautifulsoup4',
        'requests'
    ],
)
