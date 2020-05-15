from setuptools import setup
setup(
    name="django-thaad",
    version='0.1.0',
    author="Luis Moncaris",
    author_email="lmoncarisg@gmail.com",
    description="Provide utils to intercept and save/redirect requests",
    long_description=open("README.md").read(),
    packages=[
        "interceptor"
    ],
    include_package_data=True,
    install_requires=[
        'Django>=3.0',
        'djangorestframework==3.11.0',
    ],
    classifiers=[
        "Development Status :: 3 - Beta",
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Framework :: Django",
    ],
    zip_safe=False
)

