from setuptools import setup, find_packages

setup(
    name="adk-posit-demo",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        'flask==3.0.0',
        'google-cloud-aiplatform>=1.36.0',
        'vertexai>=0.0.1',
        'pandas>=2.1.0',
        'plotly>=5.17.0',
        'python-dotenv>=1.0.0',
        'numpy>=1.24.0',
        'google-cloud-storage>=2.10.0',
        'PyYAML>=6.0.1',
    ],
    python_requires='>=3.9',
)