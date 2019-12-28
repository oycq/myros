sudo pip install opencv-contrib-python                                      
sudo pip install sharedarray
sudo apt install ros-melodic-joy

sudo gpasswd --add ${USER} dialout

bind dev
udevadm info --name=/dev/ttyUSB0 |grep ID
looking at ID_MODEL_ID and ID_VENDOR_ID
sudo vim etc/udev/rules.d/10-local.rules
->
ACTION=="add", ATTRS{idVendor}=="10c4", ATTRS{idProduct}=="ea60", SYMLINK+="gimbal_uart",MODE="0666"
ACTION=="add", ATTRS{idVendor}=="0403", ATTRS{idProduct}=="6001", SYMLINK+="dji_uart",MODE="0666"
ACTION=="add", KERNEL=="js[0-9]*", ATTRS{idVendor}=="044f", ATTRS{idProduct}=="0402", SYMLINK+="j0"
ACTION=="add", KERNEL=="js[0-9]*", ATTRS{idVendor}=="044f", ATTRS{idProduct}=="0404", SYMLINK+="j1"
then replug the device

Dji_ros
1---- dji_sdk
unzip dji_sdk.zip
(git clone https://github.com/dji-sdk/Onboard-SDK)
mkdir build
cmake ..
make 
sudo make install
2--- ros
git clone https://github.com/dji-sdk/Onboard-SDK-ROS.git
cd ~/catkin_ws
sudo apt install ros-melodic-nmea-msgs
catkin_make
3--- launchfile
vim ~/catkin_ws/src/Onboard-SDK-ROS/dji_sdk/launch/sdk.launch
app_id 1080161
enc_key e362a40fba4052397389b31fc0ed8fed9df9db7890d9c06dcd1ae7d1a5a9e874
uart dji_uart

ros_network
nm-connection-editor
server:export ROS_IP=10.42.0.120
client:export ROS_IP=10.42.0.1
client:export ROS_MASTER_URI=http://10.42.0.120:11311

Realsense
sudo apt-key adv --keyserver keys.gnupg.net --recv-key F6E65AC044F831AC80A06380C8B3A55A6F3EFCDE || sudo apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv-key
sudo add-apt-repository "deb http://realsense-hw-public.s3.amazonaws.com/Debian/apt-repo bionic main" -u
sudo apt-get install librealsense2-dkms
sudo apt-get install librealsense2-utils
cd ~/catkin_ws/src/
git clone https://github.com/IntelRealSense/realsense-ros.git
cd realsense-ros/
git checkout `git tag | sort -V | grep -P "^\d+\.\d+\.\d+" | tail -1`
cd ..
sudo apt install ros-melodic-ddynamic-reconfigure
catkin_make

100G
https://www.mellanox.com/page/products_dyn?product_family=26&mtag=linux_sw_drivers

mellanox
download 4.7-3.2.9.0
https://www.mellanox.com/page/products_dyn?product_family=26&mtag=linux_sw_drivers
disable removing
sudo ./mlnxofedinstall --without-libmlx4-1 --without-libmlx5-1 --without-librxe-1
sudo /etc/init.d/openibd restart
sudo mlxfwmanager 
PCI Device Name:  0000:1a:00.0
sudo mlxconfig -d 0000:1a:00.0 set LINK_TYPE_P1=2 LINK_TYPE_P2=2

