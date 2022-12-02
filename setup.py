from setuptools import setup


setup(
    name='postrider',
    install_requires=[
        'minicli',
    ],
    extras_require={
        'test': [
            'pytest',
        ]
    }
)
