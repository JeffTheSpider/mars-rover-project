from setuptools import setup

package_name = 'rover_perception'

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
    description='Object detection and depth estimation for the Mars Rover',
    license='Apache-2.0',
    entry_points={
        'console_scripts': [
            'yolo_node = rover_perception.yolo_node:main',
            'camera_manager = rover_perception.camera_manager:main',
            'depth_processor = rover_perception.depth_processor:main',
        ],
    },
)
