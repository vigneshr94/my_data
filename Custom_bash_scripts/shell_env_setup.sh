#!/bin/bash

oh_my_zsh="$HOME/.oh_my_zsh"
os_type=$(uname -a | cut -d ' ' -f 1)
read -p "Enter Your EMAIL to generate ssh keys: " EMAIL
read -p "Do you want to install tmux: " TMUX

update_repos(){
    sudo apt update
    sudo apt upgrade -y
}

install_dependencies() {
    if [ "$os_type" == "Linux" ]; then
        if [ -x "$(command -v zsh)" ]; then
            echo "ZSH is already installed"
        else
            echo "ZSH installation is not found, installing zsh"
            sudo apt update
            sudo apt install zsh zsh-common -y
        fi
        if [ -x "$(command -v curl)" ]; then
            echo "curl installation not found"
        else
            sudo apt install curl -y
        fi
        if [ -x "$(command -v wget)"]; then
            echo "wget installation is not found" 
        else
            sudo apt install wget -y
        fi
        if [ -x "$(command -v git)"]; then
            echo "git installation is not found" 
        else
            sudo apt install git -y 
        fi
    elif [ "$os_type" == "Darwin" ]; then
        if [ -x "$(command -v zsh)" ]; then
            echo "ZSH is already installed"
        else
            echo "ZSH installation is not found, installing zsh"
            brew install zsh zsh-common -y
        fi
        if [ -x "$(command -v curl)" ]; then
            echo "curl installation not found"
        else
            brew install curl -y
        fi
        if [ -x "$(command -v wget)"]; then
            echo "wget installation is not found" 
        else
            brew install wget -y
        fi
        if [ -x "$(command -v git)"]; then
            echo "git installation is not found" 
        else
            brew install git -y 
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

install_tmux() {
    if [ $os_type == "Linux" ]; then
        sudo apt install tmux -y
    elif [ $os_type == "Darwin" ]; then
        brew install tmux
    fi
    git clone https://github.com/gpakosz/.tmux.git
    cp .tmux/.tmux.conf.local ~/
    cp .tmux/.tmux.conf ~/
}

if [ $os_type == "Linux" ]; then
    update_repos
fi
install_dependencies
install_ohmyzsh
install_omz_plugings
generate_ssh_key
install_poetry
install_docker
if [ "$tmux" == "yes" ]; then
    install_tmux
fi

