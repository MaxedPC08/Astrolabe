# Update the package list
sudo apt-get update

# Install git
sudo apt-get install -y git

# Install prerequisites for adding a new Python version
sudo apt-get install -y software-properties-common

# Add the deadsnakes PPA (contains newer Python versions)
sudo add-apt-repository ppa:deadsnakes/ppa

# Update the package list again
sudo apt-get update

# Install Python dependencies
sudo apt install -y python3-pip
sudo apt-get install -y python3-opencv
sudo apt-get install -y python3-numpy
sudo apt-get install -y python3-pil

# Clone the repository
git clone https://github.com/DroneDude1/Astrolabe.git
cd Astrolabe || exit

# Delete all items except the Coprocessor directory
find . -mindepth 1 -maxdepth 1 ! -name 'Coprocessor' -exec rm -rf {} +

# Build and install apriltag
cd Coprocessor/apriltag || exit
mkdir build
cd build || exit
cmake .. -DCMAKE_BUILD_TYPE=Release
make -j4
sudo make install
cd ../..

