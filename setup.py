import io
import os

from setuptools import setup

README = os.path.join(os.path.abspath(os.path.dirname(__file__)), "README.md")
with io.open(README, encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="pypprof",
    version="0.0.1",
    description="Python profiler endpoints like Go's net/http/pprof.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    platforms=["Mac OS X", "POSIX"],
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU Lesser General Public License v3 (LGPLv3)",
        "Operating System :: POSIX",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: Implementation :: CPython",
        "Topic :: Software Development :: Testing",
        "Topic :: Software Development :: Libraries :: Python Modules"
    ],
    project_urls={
        "Source": "https://github.com/timpalpant/pypprof",
        "Tracker": "https://github.com/timpalpant/pypprof/issues",
    },
    keywords="profiling performance",
    url="http://github.com/timpalpant/pypprof",
    author="Timothy Palpant",
    author_email="tim@palpant.us",
    license="LGPLv3",
    packages=["pypprof"],
    package_data={"pypprof": ["index.html"]},
    install_requires=["protobuf", "mprofile", "six", "zprofile"],
    test_suite="test",
)
