from setuptools import setup

package_name = 'rover_teleop'

setup(
    name=package_name,
    version='0.1.0',
    packages=[package_name],
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='Charlie',
    maintainer_email='charlie@rover.local',
    description='Web-based and gamepad teleoperation for the Mars Rover',
    license='Apache-2.0',
    entry_points={
        'console_scripts': [
            'web_server_node = rover_teleop.web_server_node:main',
            'joy_mapper = rover_teleop.joy_mapper:main',
        ],
    },
)
