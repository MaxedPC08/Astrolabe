# Update the package list
sudo apt-get update

# Install git
sudo apt-get install -y git

# Install prerequisites for adding a new Python version
sudo apt-get install -y software-properties-common

# Install library for the RPI camera
sudo apt install -y python3-picamera2 --no-install-recommends # ending flag indicates not to install GUI packages

# Add the deadsnakes PPA (contains newer Python versions)
sudo add-apt-repository ppa:deadsnakes/ppa

# Update the package list again
sudo apt-get update

# Install Python dependencies
sudo apt install -y python3-pip
sudo apt-get install -y python3-opencv
sudo apt-get install -y python3-numpy
sudo apt-get install -y python3-pil
sudo apt-get install -y python3-websockets
sudo apt-get install -y cmake

# Clone the repository
if timeout 5s git clone https://github.com/MaxedPC08/Astrolabe.git Astrolabe; then
    echo "Repository cloned successfully."
else
    echo "Failed to clone repository. Please check the URL and your network connection.
    This is likely due to misconfigured ipv4 settings. Not to worry: attempting to clone via ipv6 proxy."
    git clone https://danwin1210.de:1443/MaxedPC08/Astrolabe
fi
cd Astrolabe || exit

# Delete all items except the Coprocessor directory
find . -mindepth 1 -maxdepth 1 ! -name 'Coprocessor' -exec rm -rf {} +

# Build and install apriltag
cd Coprocessor || exit

if timeout 5s git clone https://github.com/swatbotics/apriltag.git Astrolabe; then
    echo "Repository cloned successfully."
else
    echo "Failed to clone repository. Please check the URL and your network connection.
    This is likely due to misconfigured ipv4 settings. Not to worry: attempting to clone via ipv6 proxy."
    git clone https://danwin1210.de:1443/swatbotics/apriltag
fi
cd apriltag || exit
mkdir build
cd build || exit
cmake .. -DCMAKE_BUILD_TYPE=Release
make -j4
sudo make install
cd ../..

# Create systemd service file
SERVICE_FILE="/etc/systemd/system/astrolabe.service"
sudo bash -c "cat > $SERVICE_FILE" <<EOL
[Unit]
Description=Run Astrolabe at startup
After=network.target

[Service]
ExecStart=sudo /usr/bin/python3 $(pwd)/main.py
WorkingDirectory=$(pwd)
StandardOutput=inherit
StandardError=inherit
Restart=always
User=$(whoami)

[Install]
WantedBy=multi-user.target
EOL

# Reload systemd manager configuration
sudo systemctl daemon-reload

# Enable the service to start on boot
sudo systemctl enable astrolabe.service

# Start the service immediately
sudo systemctl start astrolabe.service

# Set up static IP
if [ -z "$1" ]; then
    echo "No IP address provided. Exiting."
    exit 1
else
    new_ip=$1
fi

if [ -z "$2" ]; then
    echo "No interface provided. Exiting."
    exit 1
else
    interface=$2
fi

# Set the new IP address
sudo ifconfig "$interface" "$new_ip" netmask 255.255.255.0

# Bring the interface up
sudo ifconfig "$interface" up

# output network information to a file for connecting to the RPI
echo "$new_ip" > ip.txt
