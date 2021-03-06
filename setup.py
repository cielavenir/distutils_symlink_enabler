from setuptools import setup

setup(
    name='distutils_symlink_enabler',
    description='Enables installing symlink',
    long_description=open("README.md").read(),
    version='0.0.0.1',
    url='https://github.com/cielavenir/distutils_symlink_enabler',
    license='PSF',
    author='cielavenir',
    author_email='cielartisan@gmail.com',
    py_modules=['distutils_symlink_enabler'],
    zip_safe=False,
    include_package_data=True,
    platforms='any',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Python Software Foundation License',
        'Operating System :: POSIX',
        'Operating System :: MacOS :: MacOS X',
        'Topic :: Software Development :: Libraries',
        'Topic :: Utilities',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: Implementation :: PyPy',
    ]
)
