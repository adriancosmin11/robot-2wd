import os
from glob import glob
from setuptools import find_packages, setup

package_name = 'motor_control'

setup(
    name=package_name,
    version='0.1.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'launch'),
            glob(os.path.join('launch', '*launch.[pxy][yma]*'))),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='miruna',
    maintainer_email='miruna@todo.todo',
    description='Motor control package for 2WD robot using pyfirmata and Arduino Mega on RPi5',
    license='MIT',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'motor_driver_node = motor_control.motor_driver_node:main',
            'stop_motors_node = motor_control.stop_motors_node:main',
        ],
    },
)
