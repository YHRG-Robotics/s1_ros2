from setuptools import find_packages, setup
from glob import glob

package_name = 's1_python'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        ('share/' + package_name + '/launch', glob('launch/*.py')),
        ('share/' + package_name + '/config', glob('config/*.yaml')),
    ],
    install_requires=['setuptools','interface'],
    zip_safe=True,
    maintainer='theseus',
    maintainer_email='12345678@qq.com',
    description='TODO: Package description',
    license='TODO: License declaration',

    entry_points={
        'console_scripts': [
            's1_python = s1_python.s1_python:main',
        ],
    },  
    
)
