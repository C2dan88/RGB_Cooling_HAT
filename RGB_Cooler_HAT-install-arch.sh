#!/bin/bash

function install_python_packages() {
    sudo pacman -Syu
    sudo pacman -S base-devel python-pip python-raspberry-gpio -y
    sudo python -m pip install --upgrade pip setuptools wheel
    sudo pip install Adafruit-SSD1306
}


# Patch Adafruit_GPIO for supplied python version
function apply_patch_for() {
    VERSION="python$1"
    PATH="/usr/local/lib/$VERSION/dist-packages/Adafruit_GPIO"
    PATCH="elif match.group(1) == 'BCM2711':\n        # Pi 4\n        return 4\n    else:"
    # replace line 108 in Platform.py with patch
    sudo sed -i "108s/else.*/$PATCH/g" "$PATH/Platform.py"
    echo "Platform.py patched for Python $1"
}

echo "Installing required python packages..."
install_python_packages

echo "Patching Adafruit_GPIO to support raspberry Pi 4..."
PYTHON_VERSION=$(python -V 2>&1 | grep -Po [0-9]\.[0-9+])
apply_patch_for $PYTHON_VERSION

echo "Downloading RGB_Cooling_HAT python scripts..."
wget https://github.com/YahboomTechnology/Raspberry-Pi-RGB-Cooling-HAT/raw/master/4.Python%20programming/RGB_Cooling_HAT.zip
unzip RGB_Cooling_HAT.zip
cd RGB_Cooling_HAT/
echo "Running RGB_Cooling_HAT.py demo script..."
python RGB_Cooling_HAT.py
