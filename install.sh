#!/bin/bash

clear_assistant_entry_bashrc() {
    cat ~/.bashrc | grep -vwE ASSISTANT_DIR > /tmp/bashrc
    # I don't know why direct writing to bashrc does not work
    mv /tmp/bashrc ~/.bashrc
}

if [[ $1 == "-u" ]]; then
    echo uninstalling
    clear_assistant_entry_bashrc
    echo "Uninstall complete"
else
    clear_assistant_entry_bashrc
    echo "You are now installing your very own Assistant..."

    echo "================================================="
    echo "Setting up Env Variable ASSISTANT_DIR..."
    echo "ASSISTANT_DIR=`pwd`" >> ~/.bashrc

    echo "Congratulations!! Your Assistant is now ready. Behave well with it. ;)"
    echo "Exiting installer"
fi
echo "NOTE: DON'T FORGET TO SOURCE YOUR BASHRC!!"
