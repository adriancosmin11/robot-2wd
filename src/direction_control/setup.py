from setuptools import find_packages, setup

package_name = 'direction_control'

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
    description='Teleop and cmd_vel publisher/subscriber for the 2WD robot on RPi5',
    license='MIT',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'cmd_vel_publisher = direction_control.cmd_vel_publisher:main',
            'cmd_vel_subscriber = direction_control.cmd_vel_subscriber:main',
        ],
    },
)
