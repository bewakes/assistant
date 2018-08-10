#!/bin/bash

check_installed() {
    echo -n Checking if $1 is installed..
    $1 --version > /dev/null 2>/dev/null
    if [[ $? != "0" ]]; then
        echo NOT INSTALLED
        echo
        echo INSTALLATION FAILED: "'$1' required. Please install it and then re-run the installer."
        exit 1
    fi
    echo INSTALLED
    echo
}

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
    echo "CHECKING REQUIREMENTS..."
    echo
    # check netcat
    #check_installed netcat
    # check vlc
    check_installed vlc
    # check youtube-dl
    check_installed youtube-dl

    echo "Setting up Env Variable ASSISTANT_DIR..."
    echo "export ASSISTANT_DIR=`pwd`/" >> ~/.bashrc
    echo

    echo "Creating virtualenv for assistant"
    virtualenv -p `which python3` ${ASSISTANT_DIR}venv
    source ${ASSISTANT_DIR}venv/bin/activate && pip install -r requirements.txt

    echo "CONGRATULATIONS!! Your Assistant is now ready. And you are more lazier. ;)"
fi
echo "NOTE: Don't forget to source your bashrc"
