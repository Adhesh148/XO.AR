# XO.AR
XO.AR = XO Game + Augmented Reality

XO.AR is a desktop AR tic-tac-toe game. It lets you play against an AI or another network player with the help by augmenting opponent player moves onto your play surface. 
It was developed as a college project that combines concepts from the fields of AR, Computer Networks, AI and Software Development (including multi-threading). 

In this project, I have relied on Digital Image Processing (DIP) techniques, implemented using OpenCV, for the realization of the AR features in the game.
Networking between players has been implemented using Socket Programming, allowing players to connect with each other following the TCP protocol. In addition, we have also integrated AI into the
application which enables single players to play against a computer AI. Implementation of the AI for the Tic-Tac-Toe is done using the Minimax Algorithm.

## Program Flow

### Player Movement Detection
Once a player has made his/her move, the program must be able to identify the movement
from the image of the board. This can be done by extracting the 9 sub-grids from the image
by passing it through the grid detection algorithm described earlier. The 9 sub-images are
then passed through template matcher and circle detection algorithms to obtain the new
board configuration. It is then compared with the previous board configuration to check
for illegal moves and then update of board happens.

### Augmentation
The final step in the game loop is the augmentation of the opponent’s move onto the
player’s grid. To do so, we require the coordinates of the grid in which the opponent’s
move was made. This coordinate information can be obtained from the grid detection
algorithm. With this coordinate information, we can easily overlay the appropriate symbol
(’X’ or ’O’) onto the board image using OpenCV functions.

### Flow Diagram
<img src="https://github.com/Adhesh148/XO.AR/assets/45142485/f55cf934-7440-420f-917d-0ffc139f3ece" width="50%" height="50%">

## GUI Components
The GUI component of our project is made using PyQt python package for desktop
application. The application consists of a single window which is simple and pretty
intuitive to use.

<img src="https://github.com/Adhesh148/XO.AR/assets/45142485/3c2d33d5-1acf-4b26-8fcb-148aff659fc4" width="50%" height="50%">

## Demo
Detailed demonstration videos of our game can be found in the below links:
1. Against AI: https://drive.google.com/file/d/1J1smCIjh3VSZi-GalTGYRYFH4CC1t1Sk/view?usp=sharing
<br />
<img src="https://github.com/Adhesh148/XO.AR/assets/45142485/cd6b1f1d-9df0-4d6f-9bad-160fcdb5db9b">
<br /> <br />
2. Against Network: https://drive.google.com/file/d/1Pc_VoFBLrrSuC2EvED7oQ8d5Wf1VBHKe/view?usp=sharing
<br /><br />
<img src="https://github.com/Adhesh148/XO.AR/assets/45142485/0611aba9-fb1d-4e60-86d4-e6fdcd4621ed">

## Challenges
Our application deals with real-time video processing, augmented reality and computer
networking, all of which present different challenges on implementation. Some of the
notable challenges that I faced are:
* Achieving low latency processing of the video was a difficult task, often causing the
application to crash. A solution to this is to set an appropriate time-delay (frame
rate) between the consecutive frame captures.
* Stability of the camera is a very important factor for accurate grid detection. If
the frame captured by the camera changes frequently, it becomes difficult to process the image and detect the grid. We can resolve this issue by keeping a copy of the
previously detected grid points and comparing them with the new grid points. If
they compare well within a given threshold, we can use the newly obtained grid
points. This takes into account the principle of temporal locality.
