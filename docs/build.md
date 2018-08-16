[Back to README](../README.md)

[REVISE]

1) To get webob v1.2+ to be in Python's path, add a webob.pth file to the /usr/lib/<python>/site-packages directory with the name of the webob egg directory in it.

2) To easily access pgadmin3 v9.4, create /etc/profile.d/postgresql.[c]sh containing:
tcsh:
setenv PATH "/usr/pgsql-9.4/bin:$PATH"
bash:
export PATH="/usr/pgsql-9.4/bin:$PATH"

3) Add Apache http/https WSGI configurations for sandbox and mapper virtual hosts:
see configuration file examples in the .../mapper/apache subdirectory.

4) Append changes from the .../mapper/etc/aliases file into the system's aliases file.

5) Add the following lines to .bashrc for sandbox and mapper users:
a) For sandbox user:
export PYTHONPATH="/u/sandbox/mapper/common"
umask 0007
b) For mapper user:
export PYTHONPATH="/u/mapper/mapper/common"
umask 0007
NOTE: This allows MTurkMappingAfrica.py to be imported from scripts running in 
      other than the .../mapper/common directory, during an *interactive* session.
      Cron daemons always need to run from the .../mapper/common directory
      because crontab ignores the .bashrc settings.

6) a) Build processmail by cd'ing to ~/mapper/processmail/src, and typing 'make' as user mapper or sandbox, and then 'make install' as root. This is necesary to process incoming emails from MTurk.
   b) Change permssions of ~/mapper/processmail directory: chmod o+rx ~/mapper/processmail

7) Build boto by logging in as root, cd'ing to ~/mapper/boto, and typing:
    ./setup.sh >setup.out 2>&1

