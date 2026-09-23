from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.conditions import IfCondition
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    rviz = LaunchConfiguration('rviz')

    config_file = PathJoinSubstitution([
        FindPackageShare('fast_lio_sam'),
        'config',
        'velodyne16.yaml',
    ])

    rviz_config = PathJoinSubstitution([
        FindPackageShare('fast_lio_sam'),
        'rviz_cfg',
        'loam_livox.rviz',
    ])

    mapping_node = Node(
        package='fast_lio_sam',
        executable='fastlio_sam_mapping',
        name='laserMapping',
        output='screen',
        parameters=[
            config_file,
            {
                'feature_extract_enable': False,
                'point_filter_num': 4,
                'max_iteration': 3,
                'filter_size_surf': 0.5,
                'filter_size_map': 0.5,
                'cube_side_length': 1000.0,
                'runtime_pos_log_enable': False,
            },
        ],
    )

    rviz_node = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz',
        arguments=['-d', rviz_config],
        output='screen',
        condition=IfCondition(rviz),
    )

    return LaunchDescription([
        DeclareLaunchArgument('rviz', default_value='true'),
        mapping_node,
        rviz_node,
    ])