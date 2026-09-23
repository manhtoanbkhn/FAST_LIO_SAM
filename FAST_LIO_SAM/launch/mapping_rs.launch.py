import os
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.conditions import IfCondition
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory


def generate_launch_description():
    pkg_share = get_package_share_directory('fast_lio_sam')
    
    rviz_arg = DeclareLaunchArgument(
        'rviz',
        default_value='true',
        description='Launch rviz2'
    )
    
    rviz = LaunchConfiguration('rviz')
    
    config_file = os.path.join(pkg_share, 'config', 'rs128.yaml')
    
    laser_mapping_node = Node(
        package='fast_lio_sam',
        executable='fastlio_sam_mapping',
        name='laserMapping',
        output='screen',
        arguments=['--ros-args', '--params-file', config_file]
    )
    
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
        laser_mapping_node,
        rviz_node,
    ])
