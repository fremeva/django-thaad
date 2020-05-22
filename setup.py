from setuptools import setup
setup(
    name="django-thaad",
    version='1.0.1',
    author="Luis Moncaris",
    author_email="lmoncarisg@gmail.com",
    description="Provide utils to intercept and save/redirect requests",
    long_description=open("README.md").read(),
    long_description_content_type='text/markdown',
    packages=[
        "interceptor",
        "interceptor.api",
    ],
    include_package_data=True,
    install_requires=[
        'Django>=3.0',
        'djangorestframework==3.11.0',
        'django-cors-headers==3.3.0'
    ],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Web Environment",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Framework :: Django :: 3.0",
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Framework :: Django",
    ],
    zip_safe=False
)

