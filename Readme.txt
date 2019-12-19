sudo pip install opencv-contrib-python                                      
sudo pip install sharedarray
sudo apt install ros-melodic-joy

bind dev
udevadm info --name=/dev/ttyUSB0 |grep ID
looking at ID_MODEL_ID and ID_VENDOR_ID
sudo vim etc/udev/rules.d/10-local.rules
->
ACTION=="add", ATTRS{idVendor}=="10c4", ATTRS{idProduct}=="ea60", SYMLINK+="gimbal_uart"
ACTION=="add", ATTRS{idVendor}=="0403", ATTRS{idProduct}=="6001", SYMLINK+="dji_uart"
ACTION=="add", KERNEL=="js[0-9]*", ATTRS{idVendor}=="044f", ATTRS{idProduct}=="0402", SYMLINK+="j0"
ACTION=="add", KERNEL=="js[0-9]*", ATTRS{idVendor}=="044f", ATTRS{idProduct}=="0404", SYMLINK+="j1"

then replug the device

