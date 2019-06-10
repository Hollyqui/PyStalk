## How to install

### install python & pip3
```markdown
  sudo apt update
  apt-get install python3
  sudo apt install python3-pip
```
### verify
```markdown
  pip3 --version 
```
### install prerequisites

```markdown
pip3 install untangle
pip3 install zeroconf
sudo apt-get install bluetooth
sudo apt-get install bluez
sudo apt-get install python-bluez
sudo apt-get install python-pip libglib2.0-dev
sudo pip install bluepy
sudo apt-get update
```

### install VLC
VLC is used to view the video stream on your laptop. To install VLC you'll also need snap, hence the two command lines.

```markdown
sudo apt install snapd
sudo snap install vlc
```

### pull the modded version from github

```markdown
git clone https://github.com/amymcgovern/pyparrot
cd pyparrot
```

## How to connect to the drone

DISCLAIMER: DO NOT PRESS THE 'RUN MY PROGRAM' BUTTON WITHOUT READING FURTHER, IT'LL START THE DRONE

Now, you'll first have to turn on the bebop 2 and connect to it's wifi. Now, you'll want to start the pyparrt_test file by typing:

```markdown
python3 ./pyparrot_test.py
```
Now, a VLC popup should open that displays a video livestream from your drone. You will also find that images of every frame are stored in the path: pyparrot/pyparrot/images.

If the stream is established you can put the drone on a 'startable' surface and press the 'run my program' button. This will let the drone take off and hover in the air. 
Now you will also want to test the 'land NOW' button, which should kill the rotors and land the drone immediately for an emergency landing.

