#!/bin/bash

# required_services=(vlc youtube-dl dunstify)
required_services=()

check_installed() {
    echo -n Checking if $1 is installed..
    $1 --version > /dev/null 2>/dev/null
    if [[ $? == "127" ]]; then
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

ASSISTANT_HOME=$HOME/.assistant
ASSISTANT_DIR=`pwd`

if [[ $1 == "-u" ]]; then
    echo uninstalling
    clear_assistant_entry_bashrc
    echo "Uninstall complete"
else
    clear_assistant_entry_bashrc
    echo "You are now installing your very own Assistant..."
    echo "CHECKING REQUIREMENTS..."
    echo
    for x in ${required_services[@]}; do
        check_installed $x
    done;

    echo "Setting up Env Variable ASSISTANT_DIR..."
    echo "export ASSISTANT_DIR=$ASSISTANT_DIR/" >> ~/.bashrc
    echo "alias assistantd=$ASSISTANT_DIR/assistantd.sh" >> ~/.bashrc
    echo "alias assistant=$ASSISTANT_DIR/assistant.sh" >> ~/.bashrc
    echo

    # install default services config, which is empty
    mkdir -p $ASSISTANT_HOME
    touch $ASSISTANT_HOME/enabled_services.list

    echo "Creating virtualenv for assistant"
    virtualenv -p `which python3` ${ASSISTANT_DIR}/venv
    source ${ASSISTANT_DIR}/venv/bin/activate && pip install -r requirements.txt

    echo "CONGRATULATIONS!! Your Assistant is now ready. And you are more lazier. ;)"
    echo "You can add/remove enabled services at $ASSISTANT_HOME/enabled_services.list"
    echo "First run the daemon: assistantd"
    echo "And run: assistant <cmd>"
fi
echo "NOTE: Don't forget to source your bashrc!!"
