from setuptools import setup, find_packages

setup(
    name='editplt',
    version='0.1.0',
    packages=['editplt'],
    author='Vigneswaran Chandrasekaran',
    author_email='vigneswaran0610@gmail.com',
    description='Save your Matplotlib plots as JSON to edit later',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/vigneswaran-chandrasekaran/editplt',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
)
