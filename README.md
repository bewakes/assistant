# assistant
I am very lazy. So, I'm going to make my assistant do things for me. 

## Requirements so far
- bash 4 (which must be already the one in newer linux versions)
- python3
- vlc
- A GOOGLE API KEY (which is used to search for songs)
- netcat (to communicate with vlc, like play/pause/next etc)

## A sample command and result 
```
>>> Welcome !! 

>> play jati maya laye pani 

>>> Playing ..  
```
This plays the song 'Jati maya laye pani' in background. 

In fact, this is the only thing that has been implemented. Just need to add `export API_KEY="<Your API key>"` in `bashrc`.  

More awesome features on the way.
