#!/bin/bash

oh_my_zsh="$HOME/.oh_my_zsh"
EMAIL="vigneshr.1894@gmail.com"

install_dependencies() {
    if [ -x "$(command -v zsh)" ]; then
        echo "ZSH is already installed"
    else
        echo "ZSH is not installed, installing zsh."
        sudo apt update
        sudo apt install zsh zsh-common curl git  -y
    fi
    if [ -x "$(command -v curl)" ]; then
        echo "Curl is already installed."
    else
        echo "Installing Curl."
        sudo apt install curl -y
    fi
    if [ -x "$(command -v git)" ]; then
        echo "Git is already isntalled."
    else
        echo "Installing Git."
        sudo apt isntall git -y
    fi
}

install_ohmyzsh() {
    if [ -d "$oh_my_zsh" ]; then
        echo "Oh My Zsh is isntalled."
    else
        echo "Oh My Zsh is not installed, installing."
        sh -c "$(wget -O- https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/install.sh)"
    fi
}

install_omz_plugings() {
    echo "Installing autosuggesions..."
    git clone https://github.com/zsh-users/zsh-autosuggestions.git $ZSH_CUSTOM/plugins/zsh-autosuggestions
    echo "Installing syntax highlighting..."
    git clone https://github.com/zsh-users/zsh-syntax-highlighting.git $ZSH_CUSTOM/plugins/zsh-syntax-highlighting
    echo "Installing fast syntax highlighting..."
    git clone https://github.com/zdharma-continuum/fast-syntax-highlighting.git ${ZSH_CUSTOM:-$HOME/.oh-my-zsh/custom}/plugins/fast-syntax-highlighting
    echo "Installing Auto complete...."
    git clone --depth 1 -- https://github.com/marlonrichert/zsh-autocomplete.git $ZSH_CUSTOM/plugins/zsh-autocomplete
}

generate_ssh_key() {
    echo "Generating ssh keys"
    ssh-keygen -t rsa -C "$EMAIL"
    echo "Key Generation Successfull"
    echo "showing public key"
    cat ~/.ssh/*.pub
}

install_dependencies
install_ohmyzsh
install_omz_plugings
generate_ssh_key
