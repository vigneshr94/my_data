#! /bin/bash

echo "Creating the swap folder"
sudo mkdir /swap

echo "Checking the swap folder"
ls -lh /

echo "Creating swap file with fallocate"
sudo fallocate -l 8G /swap/swapfile

echo "Checking the the swapfile size"
ls -lh /swap/swapfile

echo "Changing swap file permissions to root user"
sudo chmod 600 /swap/swapfile

echo "Turning on the swap"
sudo mkswap /swap/swapfile
sudo swapon /swap/swapfile

echo "Viewing swap status"
sudo swapon --show

echo "Making swap permenant"
echo "Taking fstab backup"
sudo cp /etc/fstab /etc/fstab.bak

echo "Adding swap to fstab"
echo '/swap/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab

echo "Viewing fstab"
cat /etc/fstab

echo "Fine Tuning swap settings"
echo "vm.swappiness=10" | sudo tee -a /etc/sysctl.conf
echo "vm.vfs_cache_pressure=50" | sudo tee -a /etc/sysctl.conf

cat /etc/sysctl.conf

echo "Applying swap settings"
sudo sysctl vm.swappiness=10
sudo sysctl vm.vfs_cache_pressure=50