#!/bin/bash

rand_song=
getrandom() {
    len=${#songs_list[@]}
    ind=$(($RANDOM%$len))
    rand_song=(${songs_list[$ind]})
}
