# assistant
I am very lazy. So, I'm going to make my assistant do things for me. 

## Requirements so far
- bash 4 (which must be already the one in newer linux versions)
- python3
- vlc(this will use commandline version)
- A GOOGLE API KEY (which is used to search for songs)
- telnet and netcat (to communicate with vlc, like play/pause/next etc)  

## current features 
- play <song_name> : plays the song from youtube
- pause : pauses the song
- play : resumes song
- play random : plays random song from your play history
- bye : exits 

*No playlists implemented though*

## A sample command and result 
```
>>> Welcome !! 

>> play jati maya laye pani 

>>> Playing ..  

```
This plays the song 'Jati maya laye pani' in background. 

## TODO: automatic installation and setup
For now, just need to add  

`export API_KEY="<Your API key>"` and  

`export ASSISTANT_DIR="<this project's directory>" ` in `bashrc`.  

More awesome features on the way.  

## CONTRIBUTIONS 
contributions are highly welcome, We'll make a 'jarvis' like being. ;).  
Go through [Implementation.md](https://github.com/bewakes/assistant/blob/master/Implementation.md)
