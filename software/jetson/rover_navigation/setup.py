from setuptools import setup

package_name = 'rover_navigation'

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
    description='Ackermann kinematics, waypoint following, and geofencing',
    license='Apache-2.0',
    entry_points={
        'console_scripts': [
            'ackermann_controller = rover_navigation.ackermann_controller:main',
            'waypoint_follower = rover_navigation.waypoint_follower:main',
            'geofence_node = rover_navigation.geofence_node:main',
        ],
    },
)
