# setup.py
from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name='ag-ai-tool',
    version='2.0.1', # 我们进入一个全新的大版本！
    author='utmux',
    author_email='example@example.com',
    description='A powerful, pipe-aware AI assistant for your shell.',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='https://github.com/utmux/ag-ai-tool',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'openai>=1.10.0',
        'click>=8.0',
        'rich>=13.0',
    ],
    # --- 【核心修改】 ---
    # 定义两个独立的命令入口点
    entry_points={
        'console_scripts': [
            'ag = ag_cli.cli:main_ask',      # 'ag' 命令指向 main_ask 函数
            'agc = ag_cli.cli:main_config',   # 'agc' 命令指向 main_config 函数
        ],
    },
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Topic :: Utilities',
        'Environment :: Console',
    ],
    python_requires='>=3.8',
)