import setuptools


with open('README.md', 'r') as readme:
    long_description = readme.read()

setuptools.setup(
    name='datanashor',
    version='0.3.0',
    author='James Jung',
    author_email='therealjamesjung@gmail.com',
    description='League of Legends live replay parser',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/fifteen-GG/DataNashor-Parser',
    license='MIT',
    packages=setuptools.find_packages(),
    keyword=['League of Legends', 'Replay', 'Parser', 'League',
             'Lol', 'Lolreplay', 'Lolreplayparser', 'Lolreplayparser', 'DataNashor', 'datanashor'],
    install_requires=['requests', 'beautifulsoup4', 'pyserial'],
    classifiers=[
        'Intended Audience :: Developers',
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: Microsoft :: Windows',
    ],
    python_requires='>=3.9',
)
