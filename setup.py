from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = fh.read().splitlines()

setup(
    name="llm-voice-agent",
    version="0.1.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="A voice-controlled assistant using Google's Gemini API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Nalwa-Jayesh/voxa",
    packages=find_packages(include=['voice_assistant', 'voice_assistant.*']),
    include_package_data=True,
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "voice-assistant=voice_assistant.main:main",
        ],
    },
) 