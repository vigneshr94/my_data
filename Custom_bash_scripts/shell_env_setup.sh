#!/bin/bash

oh_my_zsh="$HOME/.oh_my_zsh"
os_type=$(uname -a | cut -d ' ' -f 1)
read -p "Enter Your EMAIL to generate ssh keys: " EMAIL

update_repos(){
    sudo apt update
    sudo apt upgrade -y
}

install_dependencies() {
    if [ -x "$(command -v zsh)" ]; then
        echo "ZSH is already installed"
    else
        echo "ZSH is not installed, installing zsh."
        if [ "$os_type" == "Linux" ]; then
            sudo apt update
            sudo apt install zsh zsh-common -y
        elif [ "$os_type" == "Darwin" ]; then
            brew install zsh
        fi
    fi
    if [ -x "$(command -v curl wget)" ]; then
        echo "Curl and wget is already installed."
    else
        echo "Installing Curl and WGET."
        if [ "$os_type" == "Linux" ]; then
            sudo apt install curl wget -y
        elif [ "$os_type" == "Darwin" ]; then
            brew install curl wget
        fi
    fi
    if [ -x "$(command -v git)" ]; then
        echo "Git is already isntalled."
    else
        echo "Installing Git."
        if [ "$os_type" == "Linux" ]; then
            sudo apt install git -y
        elif [ "$os_type" == "Darwin" ]; then
            brew install git
        fi
    fi
}

install_ohmyzsh() {
    if [ -d "$oh_my_zsh" ]; then
        echo "Oh My Zsh is installed."
    else
        echo "Oh My Zsh is not installed, installing."
        sh -c "$(wget -O- https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/install.sh)"
    fi
}

install_omz_plugings() {
    echo "Installing autosuggesions..."
    git clone https://github.com/zsh-users/zsh-autosuggestions.git ${ZSH_CUSTOM:-$HOME/.oh-my-zsh/custom}/plugins/zsh-autosuggestions
    echo "Installing syntax highlighting..."
    git clone https://github.com/zsh-users/zsh-syntax-highlighting.git ${ZSH_CUSTOM:-$HOME/.oh-my-zsh/custom}/plugins/zsh-syntax-highlighting
    echo "Installing fast syntax highlighting..."
    git clone https://github.com/zdharma-continuum/fast-syntax-highlighting.git ${ZSH_CUSTOM:-$HOME/.oh-my-zsh/custom}/plugins/fast-syntax-highlighting
    echo "Installing Auto complete...."
    git clone --depth 1 -- https://github.com/marlonrichert/zsh-autocomplete.git ${ZSH_CUSTOM:-$HOME/.oh-my-zsh/custom}/plugins/zsh-autocomplete
}

generate_ssh_key() {
    echo "Generating ssh keys"
    ssh-keygen -t rsa -C "$EMAIL"
    echo "Key Generation Successfull"
    echo "showing public key"
    cat ~/.ssh/*.pub
}

install_poetry() {
    echo "Installing Poetry"
    curl -sSL https://install.python-poetry.org | python3 -
    echo "Poetry Successfully intalled, Please add it to the path"
}

install_docker() {
    echo "Installing Docker"
    curl -fsSL https://get.docker.com -o get-docker.sh
    sudo sh ./get-docker.sh
    sudo usermod -aG docker $USER
    echo "Docker Successfully installed. Logout and login to use docker without sudo."
}


if [$os_type == "Linux"]; then
    update_repos
fi
install_dependencies
install_ohmyzsh
install_omz_plugings
generate_ssh_key
install_poetry
install_docker
