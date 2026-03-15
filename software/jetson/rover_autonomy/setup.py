import os
from glob import glob
from setuptools import setup

package_name = 'rover_autonomy'

setup(
    name=package_name,
    version='0.1.0',
    packages=[package_name],
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'behaviour_trees'),
            glob('behaviour_trees/*.xml')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='Charlie',
    maintainer_email='charlie@rover.local',
    description='Autonomous mission planning and behaviour trees',
    license='Apache-2.0',
    entry_points={
        'console_scripts': [
            'mission_planner = rover_autonomy.mission_planner:main',
        ],
    },
)
