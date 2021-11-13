#!/bin/bash

# Colors
end="\033[0m"
black="\033[0;30m"
blackb="\033[1;30m"
white="\033[0;37m"
whiteb="\033[1;37m"
red="\033[0;31m"
redb="\033[1;31m"
green="\033[0;32m"
greenb="\033[1;32m"
yellow="\033[0;33m"
yellowb="\033[1;33m"
blue="\033[0;34m"
blueb="\033[1;34m"
purple="\033[0;35m"
purpleb="\033[1;35m"
lightblue="\033[0;36m"
lightblueb="\033[1;36m"

function red {
  echo -e "${red}${1}${end}"
}

function green {
  echo -e "${green}${1}${end}"
}

function yellow {
  echo -e "${yellow}${1}${end}"
}

function install_required_packages() {
    sudo apt-get update && sudo apt-get install build-essential python3-pip python3-dev git
    # upgrade and install required packages
    python3 -m pip install --upgrade pip setuptools wheel
    export CFLAGS=-fcommon
    sudo pip3 install Pillow psutil smbus rpi-gpio Adafruit-SSD1306

    # add user to i2c group
    sudo usermod -aG i2c pi

    echo "Downloading RGB Cooling HAT scripts..."
    git clone http://github.com/C2dan88/RGB_Cooling_HAT.git
    cd RGB_Cooling_HAT
}


# Patch Adafruit_GPIO for python version
function apply_patch_for() {
    VERSION="python$1"
    PKG_PATH="/usr/local/lib/$VERSION/dist-packages/Adafruit_GPIO"
    FILE="$PKG_PATH/Platform.py"
    PATCH="elif match.group(1) == 'BCM2711':\n        # Pi 4\n        return 4\n    else:"
    # replace line 108 in Platform.py with patch
    if test -f "$FILE"; then
    	sudo sed -i "108s/else.*/$PATCH/g" "$PKG_PATH/Platform.py"
    	green("$FILE patched for Python $1")
    else
    	 red("$FILE does not exist!!!!!!")
    fi
}

function install_cooler_service() {
    sudo cp cooler.service /etc/systemd/system/
    echo "Starting cooler..."
    sudo systemctl start cooler
    sudo systemctl enable cooler
}

echo "Installing required packages..."
install_required_packages

echo "Patching Adafruit_GPIO to support raspberry Pi 4..."
PYTHON_VERSION=$(python3 -V 2>&1 | grep -Po [0-9]\.[0-9+])
apply_patch_for $PYTHON_VERSION

echo "Creating cooler service..."
install_cooler_service

green("... DONE ...")
