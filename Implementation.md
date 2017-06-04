## How it is being implemented(till now, might change later) 

Main file is **assistant.sh.** 

There are different **services** available under **services/** folder. 

After being run, **assistant.sh** will be parent process, which will create child processes for each of the services(python programs).  

The parent will take in commands from user and communicate it to the appropriate service through the use of sockets. Later, I am planning
 to user named pipes for IPC.
