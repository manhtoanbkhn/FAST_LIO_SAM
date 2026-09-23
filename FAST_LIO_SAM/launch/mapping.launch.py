import os
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.conditions import IfCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare
from ament_index_python.packages import get_package_share_directory


def generate_launch_description():
    # Get package directory
    pkg_share = get_package_share_directory('fast_lio_sam')
    
    # Declare launch arguments
    rviz_arg = DeclareLaunchArgument(
        'rviz',
        default_value='true',
        description='Launch rviz2'
    )
    
    config_file_arg = DeclareLaunchArgument(
        'config_file',
        default_value=os.path.join(pkg_share, 'config', 'avia.yaml'),
        description='Path to config YAML file'
    )
    
    # Map config file name to launch
    config_file = LaunchConfiguration('config_file')
    rviz = LaunchConfiguration('rviz')
    
    # Main node
    laser_mapping_node = Node(
        package='fast_lio_sam',
        executable='fastlio_sam_mapping',
        name='laserMapping',
        output='screen',
        arguments=['--ros-args', '--params-file', config_file]
    )
    
    # Rviz node
    rviz_config_file = os.path.join(pkg_share, 'rviz_cfg', 'loam_livox.rviz')
    rviz_node = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz',
        arguments=['-d', rviz_config_file],
        condition=IfCondition(rviz),
        prefix='nice'
    )
    
    return LaunchDescription([
        rviz_arg,
        config_file_arg,
        laser_mapping_node,
        rviz_node,
    ])
