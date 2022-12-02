from setuptools import setup


setup(
    name='postrider',
    install_requires=[
        'minicli',
        'dynaconf',
    ],
    extras_require={
        'test': [
            'pytest',
        ]
    }
)
