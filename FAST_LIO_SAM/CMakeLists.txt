cmake_minimum_required(VERSION 3.8)
project(fast_lio_sam)

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

add_definitions(-DROOT_DIR=\"${CMAKE_CURRENT_SOURCE_DIR}/\")

# OpenMP
find_package(OpenMP QUIET)
if(OpenMP_CXX_FOUND)
  set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} ${OpenMP_CXX_FLAGS}")
  set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} ${OpenMP_C_FLAGS}")
endif()

# Python (for matplotlibcpp)
find_package(PythonLibs REQUIRED)
find_path(MATPLOTLIB_CPP_INCLUDE_DIRS "matplotlibcpp.h")

# Multi-core processing
include(ProcessorCount)
ProcessorCount(N)
if(N GREATER 4)
  add_definitions(-DMP_EN)
  add_definitions(-DMP_PROC_NUM=3)
elseif(N GREATER 3)
  add_definitions(-DMP_EN)
  add_definitions(-DMP_PROC_NUM=2)
else()
  add_definitions(-DMP_PROC_NUM=1)
endif()

# ROS 2 dependencies
find_package(ament_cmake REQUIRED)
find_package(rclcpp REQUIRED)
find_package(std_msgs REQUIRED)
find_package(sensor_msgs REQUIRED)
find_package(nav_msgs REQUIRED)
find_package(geometry_msgs REQUIRED)
find_package(visualization_msgs REQUIRED)
find_package(tf2_ros REQUIRED)
find_package(tf2_geometry_msgs REQUIRED)
find_package(pcl_ros REQUIRED)
find_package(pcl_conversions REQUIRED)
find_package(livox_ros_driver REQUIRED)
find_package(rosidl_default_generators REQUIRED)
find_package(tf2_eigen REQUIRED)

# Eigen3
find_package(Eigen3 REQUIRED)
# PCL
find_package(PCL REQUIRED)
# GeographicLib
list(APPEND CMAKE_MODULE_PATH "/usr/share/cmake/geographiclib")
find_package(GeographicLib REQUIRED)
# GTSAM
find_package(GTSAM REQUIRED QUIET)

message(STATUS "Eigen: ${EIGEN3_INCLUDE_DIR}")

# Generate custom messages and services
rosidl_generate_interfaces(${PROJECT_NAME}
  "msg/Pose6D.msg"
  "srv/SaveMap.srv"
  "srv/SavePose.srv"
  DEPENDENCIES std_msgs geometry_msgs
)

# Include directories
include_directories(
  ${EIGEN3_INCLUDE_DIR}
  ${PCL_INCLUDE_DIRS}
  ${PYTHON_INCLUDE_DIRS}
  ${GTSAM_INCLUDE_DIR}
  ${GeographicLib_INCLUDE_DIRS}
  include
  src
)

# Libraries
add_library(ikd_Tree include/ikd-Tree/ikd_Tree.cpp)
target_link_libraries(ikd_Tree ${PCL_LIBRARIES})

add_library(preprocess src/preprocess.cpp)
target_link_libraries(preprocess ${PCL_LIBRARIES})

ament_target_dependencies(preprocess
  rclcpp
  sensor_msgs
  livox_ros_driver
  pcl_conversions
)

# Get message types
rosidl_get_typesupport_target(cpp_typesupport_target ${PROJECT_NAME} "rosidl_typesupport_cpp")

# Main executable
add_executable(fastlio_sam_mapping src/laserMapping.cpp)
target_link_libraries(fastlio_sam_mapping
  ${PCL_LIBRARIES}
  ${PYTHON_LIBRARIES}
  ${GeographicLib_LIBRARIES}
  gtsam
  ikd_Tree
  preprocess
  ${cpp_typesupport_target}
)
ament_target_dependencies(fastlio_sam_mapping
  rclcpp
  std_msgs
  sensor_msgs
  nav_msgs
  geometry_msgs
  visualization_msgs
  tf2_ros
  tf2_geometry_msgs
  pcl_ros
  pcl_conversions
  livox_ros_driver
  tf2_eigen
)

target_include_directories(fastlio_sam_mapping PRIVATE ${PYTHON_INCLUDE_DIRS})

# Install
install(TARGETS fastlio_sam_mapping ikd_Tree preprocess
  ARCHIVE DESTINATION lib
  LIBRARY DESTINATION lib
  RUNTIME DESTINATION lib/${PROJECT_NAME}
)

install(DIRECTORY launch/
  DESTINATION share/${PROJECT_NAME}/launch
)

install(DIRECTORY config/
  DESTINATION share/${PROJECT_NAME}/config
)

install(DIRECTORY rviz_cfg/
  DESTINATION share/${PROJECT_NAME}/rviz_cfg
)

ament_package()
