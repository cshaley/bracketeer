from setuptools import setup, find_packages
import bracketeer

setup(
    name='bracketeer',
    description='Python Library for testing march madness brackets',
    version=bracketeer.__version__,
    author='Charlie Haley',
    author_email='charlie.haley@gmail.com',
    url='https://github.com/cshaley/bracketeer',
    download_url='https://github.com/cshaley/bracketeer/archive/0.1.0.tar.gz',
    packages=find_packages(),
    package_data={'bracketeer': ['bracketeer/empty_brackets/*.jpg', 'bracketeer/tests/input/*.csv']},
    install_requires=["pandas", "binarytree", "matplotlib", "Pillow"],
    include_package_data=True,
    license='MIT',
    classifiers=[
        'Intended Audience :: Developers',
        'Intended Audience :: End Users/Desktop',
        'Intended Audience :: Information Technology',
        'License :: OSI Approved :: MIT License',
        'Operating System :: POSIX',
        'Operating System :: MacOS',
        'Operating System :: Unix',
        'Operating System :: Microsoft :: Windows',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.6',
    ]
)
