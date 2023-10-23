#!/bin/bash

install_dependencies() {
    if [ -x "$(command -v zsh)" ]; then
        echo "ZSH is already installed"
    else
        echo "ZSH is not installed, installing zsh."
        apt update
        apt install zsh zsh-common curl git  -y
    fi
    if [ -x "$(command -v curl)" ]; then
        echo "Curl is already installed."
    else
        echo "Installing Curl."
        apt install curl -y
    fi
    if [ -x "$(command -v git)" ]; then
        echo "Git is already isntalled."
    else
        echo "Installing Git."
        apt isntall git -y
    fi
}


oh_my_zsh="$HOME/.oh_my_zsh"

install_ohmyzsh() {
    if [ -d "$oh_my_zsh" ]; then
        echo "Oh My Zsh is isntalled."
    else
        echo "Oh My Zsh is not installed, installing."
        sh -c "$(curl -fsSL https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/install.sh)"
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

install_dependencies
install_ohmyzsh
install_omz_plugings
