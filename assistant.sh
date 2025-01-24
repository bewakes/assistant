#!/bin/bash
source "$ASSISTANT_DIR"/helpers.sh

TMP_DIR=/tmp/assistant
SERVICES_DIR=$TMP_DIR/services
LOCK_FILE=$TMP_DIR/assistant.lock
ASSISTANT_HOME=$HOME/.assistant

kill_services() {
    for s in $(ls $SERVICES_DIR); do
        pid=$(head -n 2 $SERVICES_DIR/$s | tail -n 1)
        echo killing $s with pid $pid;
        kill -9 $pid
    done
}

execute_command() {
    case $1 in
        "greet")
            echo How may I help you?
            ;;
        "exit")
            kill_services
            rm -rf $TMP_DIR
            echo exiting
            ;;
        "quiz")
            execute_command llm $@
            port=$(head -n 1 $SERVICES_DIR/llm)
            exec 3<>/dev/tcp/localhost/$port

            echo $@ >&3

            ## read data from the socket
            read -r tmp <&3
            echo $tmp
            ;;
        "pause")
            execute_command vlc $@
            #echo -e "test\npause\nquit" | nc localhost 4212
            ;;
        "play")
            execute_command vlc $@
            ;;
        "playlist")
            execute_command vlc $@
            ;;
        "next")
            execute_command vlc $@
            ;;
        "previous")
            execute_command vlc $@
            ;;
        "repeat")
            execute_command vlc $@
            ;;
        "stop")
            msg="Stopped"
            ;;
        "vlc")
            exec 3<>/dev/tcp/localhost/${ports["vlc"]}

            ## send to socket
            shift
            echo $@ >&3

            ## read data from the socket
            read -r tmp <&3
            msg=$tmp
            ;;
        "bye")
            cleanup
            exit 0
            ;;
        "exit")
            cleanup
            exit 0
            ;;
        "list")
            echo "LIST OF SONGS"
            cat $HOME/.assistant/songs
            echo $songs
            ;;
        "meaning")
            exec 3<>/dev/tcp/localhost/${ports["meaning"]}
            echo $@ >&3
            msg=$(cat<&3)
            ;;
        "translate")
            exec 3<>/dev/tcp/localhost/${ports["translate"]}
            echo $@ >&3
            msg=$(cat<&3)
            ;;
        "translateto")
            exec 3<>/dev/tcp/localhost/${ports["translate"]}
            echo $@ >&3
            msg=$(cat<&3)
            ;;

        "download")
            exec 3<>/dev/tcp/localhost/${ports["song_download"]}
            echo $@ >&3
            msg=$(cat<&3)
            ;;
        "clear")
            clear >$(tty)
            msg=""
            ;;
        "list_services")
            echo Services Available: ${services[@]}
            msg=""
            ;;
        "set_context")
            echo setting context $2
            msg=""
            context=$2
            ;;
        "clear_context")
            echo Getting out of "$context" context 
            context=
            msg=''
            ;;
        "which_context")
            if [[ $context == "" ]]; then
                echo No context set
            else
                echo Your are in the $context context 
            fi
            msg=''
            ;;
        "note")
            exec 3<>/dev/tcp/localhost/${ports["notes"]}
            shift
            echo $@ >&3
            msg=$(cat<&3)
            ;;
        "notes")
            shift
            execute_command note $@
            ;;
        "calc")
            exec 3<>/dev/tcp/localhost/${ports["calc"]}
            echo "$@" >&3
            msg=$(cat<&3)
            ;;
        "reminder")
            exec 3<>/dev/tcp/localhost/${ports["reminder"]}
            shift
            echo $@ >&3
            msg=$(cat<&3)
            ;;
        "expense")
            exec 3<>/dev/tcp/localhost/${ports["expense"]}
            shift
            echo $@ >&3
            msg=$(cat<&3)
            ;;
        "todo")
            exec 3<>/dev/tcp/localhost/${ports["todo"]}
            shift
            echo $@ >&3
            msg=$(cat<&3)
            ;;
        "pomodoro")
            exec 3<>/dev/tcp/localhost/${ports["pomodoro"]}
            shift
            echo $@ >&3
            msg=$(cat<&3)
            ;;
        *)
            if [[ $context != "" ]]; then
                execute_command $context $@
            else
                msg="Command not recognized"
            fi
            ;;
    esac
}

execute_command $@


# TODO: RUN THE FOLLOWING IF INTERACTIVE
# while true; do
#     if [[ $msg != "" ]]; then
#         echo -e $prompt"$msg"
#     fi
#     echo -n ">> "
#     read -a command_args
#     cmnd=${command_args[0]}
#     args=${command_args[@]:1} # getting rest of the array
#     execute_command $cmnd "$args"
# done
