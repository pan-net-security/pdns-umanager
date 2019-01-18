from setuptools import setup

setup(
    name='pdnsumanager',
    version='0.0.1',
    description='A PDNS micro manager tool for the poor',
    author='Diogenes Santos de Jesus',
    author_email='diogenes.jesus@pan-net.eu',
    url='https://github.com/pan-net-security/pdns-umanager',
    packages=['pdnsumanager'],
    install_requires=['requests',
                      'pyaml'
                      ],
    keywords=['ci', 'devops', 'automation'],
    classifiers=[
        'Environment :: Console',
        'Programming Language :: Python :: 3',
        'Operating System :: OS Independent',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'License :: OSI Approved :: MIT License',
    ],
    entry_points={'console_scripts': ['pdns-umanager = pdnsumanager.pdnsumanager:main']},
)
