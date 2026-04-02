from setuptools import find_packages, setup

package_name = 'control_cu_functii'

setup(
    name=package_name,
    version='0.1.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='miruna',
    maintainer_email='miruna@todo.todo',
    description='Standalone motor test node using pyfirmata functions (2WD robot, RPi5)',
    license='MIT',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'motor_test_node = control_cu_functii.motor_test_node:main',
        ],
    },
)
