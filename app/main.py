from app import Ui_MainWindow
import sys
import os
import time
import socket
from PyQt5.QtCore import pyqtSignal, QThread
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import threading

from PyQt5 import QtTest

import cv2

from grid_detect import getGridPts,getGridImage, isGridFilled, containsCircle, getGrids, containsCross
from tic_tac_toe import areMovesLeft, evaluate, minimax, findBestMove

# Camera Related Parameters
CAM_STATE = 0

# Game Related Parameters
GAME_STATUS = 0                 # 0 - inactive; 1 - active; 
TURN = 0                        # 0 represents opponents turn and 1 represents PLAYERs turn
PLAY_MODE = 0                   # 0 - with AI; 1 - with network opponent
MOVED = 0
OPPONENT_MOVED = 0

# Player variables
PLAYER = 'o'
OPPONENT = 'x'

# Network Game Related parameters
join_status = 0

board = [['_','_','_'],['_','_','_'],['_','_','_']]
grid_coordinates = []

# Fixed Network Connection Parameters
HEADER = 64
FORMAT = 'utf-8'
DISCONNECT_MSG = "!END"

test_client = socket.socket()

OVERLAY_TEXT = ''

board_img = []

class MainWindow(QMainWindow, Ui_MainWindow):

	global_client = socket.socket()

	def __init__(self, parent=None):
		QMainWindow.__init__(self, parent=parent)
		self.setupUi(self)

		# add listener to connect to cam button
		self.cam_connect_btn.clicked.connect(lambda: self.connectToCamera())

		# add listener to "join" button
		self.join_btn.clicked.connect(lambda: self.connectToGameRoom())

		# add listener to "join ai" button
		self.ai_btn.clicked.connect(lambda: self.connectToAi())

	def keyPressEvent(self, e):
		global MOVED, GAME_STATUS, TURN
		if GAME_STATUS == 1 and TURN == 1:
			if e.key() == 32:
				MOVED = 1
				print('Moved')
		
		print(e.key())

	def connectToAi(self):

		global PLAY_MODE, TURN, PLAYER, opponent, GAME_STATUS, board, board_img, MOVED, grid_coordinates

		# Step - 1: Make sure cam is started

		# Step - 1.5: Get the grid coordinates and store them
		grid_coordinates = getGridPts(board_img)

		# Step - 2: Disable Network Buttons

		# Step - 3: Validate & Start Game
		self.system_stat_edit.setText(f'Cam Status: {1};  Game Status: {GAME_STATUS};  Turn: {TURN};  Player: {PLAYER}')
		PLAY_MODE = 0																			# 0 => Against AI
		TURN = 1																				# 1 => User Plays First
		GAME_STATUS = 1																			# 1 => Game is Active
		board = [['_','_','_'],['_','_','_'],['_','_','_']] 									# Intialize the board
		PLAYER = 'o'																			# User is 'O' - convinient
		opponent = 'x'																			# Opponent is therefore 'X'
		print(board)																			# Display the board initially

		# Step - 3.5: Overlay Start Status
		#self.blockingOverlay()

		# Step - 4: Enter Game Loop
		while(GAME_STATUS == 1):

			# If player's Turn => Wait for player to make the move
			if TURN == 1:

				# Wait for player
				while MOVED == 0:
					QtTest.QTest.qWait(30)
					continue

				# Identify Move and update board
				#print('HERE')
				while self.identifyMove(board_img,grid_coordinates)[1] == False:
					QtTest.QTest.qWait(30)
					continue
				
				print(board)
				MOVED = 0

				# Once play is made, switch turns to AI
				TURN = 0

			else:

				# AI makes its move
				best_move = findBestMove(board, player=OPPONENT, opponent=PLAYER)
				print(best_move)
				board[best_move[0]][best_move[1]] = OPPONENT
				print(board)

				QtTest.QTest.qWait(1000)

				# Switch turns
				TURN = 1

			# At end of each turn, check the status of the board
			status = self.getGameStatus(board)

			if status == -1:
				# Tie condition - print result and stop game
				print('Game is Tied')
				self.blockingOverlay('Tie',3)
				GAME_STATUS = 0

			elif status == 10 or status == -10:
				if TURN == 0:
					# User wins the game & stop the game
					print('You Win')
					self.blockingOverlay('Victory',3)

				else:
					# User wins the game & stop the game
					print('You Lose')
					self.blockingOverlay('You Lose',3)
				
				QtTest.QTest.qWait(3000)
				GAME_STATUS = 0

			else:
				if TURN == 1:
					print('Your Turn')
					self.blockingOverlay('Your Turn',2)
				else:
					print('Opponents Turn')
					self.blockingOverlay('AIs Turn',2)

			self.system_stat_edit.setText(f'Cam Status: {1};  Game Status: {GAME_STATUS};  Turn: {TURN};  Player: {PLAYER}')

	def connectToNetworkGame(self):
		global PLAY_MODE, TURN, PLAYER, OPPONENT, GAME_STATUS, board, board_img, MOVED, grid_coordinates, OPPONENT_MOVED

		# Step - 1: Make sure cam is started

		# Step - 1.5: Get the grid coordinates and store them
		grid_coordinates = getGridPts(board_img)

		# Wait for Game to Start
		while GAME_STATUS == 0:
			QtTest.QTest.qWait(30)
			print(GAME_STATUS)
			continue

		#print('AFTER BLOVK')
		# Step - 3: Validate & Start Game
		PLAY_MODE = 1																			# 1 => Against Network
		board = [['_','_','_'],['_','_','_'],['_','_','_']] 									# Intialize the board
		print(board)																			# Display the board initially

		self.system_stat_edit.setText(f'Cam Status: {1};  Game Status: {GAME_STATUS};  Turn: {TURN};  Player: {PLAYER}')

		# Enter Game Loop
		while GAME_STATUS == 1:

			# If player's Turn => Wait for player to make the move
			if TURN == 1:

				# Wait for player
				while MOVED == 0:
					QtTest.QTest.qWait(30)
					continue

				# Identify Move and update board
				move, board_status = self.identifyMove(board_img,grid_coordinates)
				while  board_status == False:
					QtTest.QTest.qWait(30)
					move, board_status = self.identifyMove(board_img,grid_coordinates)
					continue
				
				print(board)
				MOVED = 0

				# Send Move to Opponent
				msg = 'move: '+str(move[0])+' '+str(move[1])
				self.sendMessage(msg)

				# Once play is made, switch turns to OPPONENT
				TURN = 0

			else:

				# Wait for OPPONENT to make the move
				while OPPONENT_MOVED == 0:
					QtTest.QTest.qWait(30)
					continue
				
				# Update Board & Overlay
				print(board)

				# Switch turns
				OPPONENT_MOVED = 0
				TURN = 1

			# At end of each turn, check the status of the board
			status = self.getGameStatus(board)

			if status == -1:
				# Tie condition - print result and stop game
				print('Game is Tied')
				self.blockingOverlay('Tie',3)
				GAME_STATUS = 0

			elif status == 10 or status == -10:
				if TURN == 0:
					# User wins the game & stop the game
					print('You Win')
					self.blockingOverlay('Victory',3)

				else:
					# User wins the game & stop the game
					print('You Lose')
					self.blockingOverlay('You Lose',3)
				
				QtTest.QTest.qWait(3000)
				GAME_STATUS = 0

			else:
				if TURN == 1:
					print('Your Turn')
					self.blockingOverlay('Your Turn',2)
				else:
					print('Opponents Turn')
					self.blockingOverlay('Opponents Turn',2)

			self.system_stat_edit.setText(f'Cam Status: {1};  Game Status: {GAME_STATUS};  Turn: {TURN};  Player: {PLAYER}')

	def getGameStatus(self,board):
		global PLAYER, OPPONENT
		
		# Check for victory condition
		score = evaluate(board, PLAYER, OPPONENT)
		if score !=0:
			return score

		# If score == 0, then check if any more moves are possible
		movesLeft = areMovesLeft(board)
		if movesLeft == True:
			return 0
		else:
			return -1

	def identifyMove(self, img, gridc):
		global board, PLAYER
		# Get the individual grid images first
		grids = getGridImage(img, gridc[0],gridc[1],gridc[2],gridc[3],gridc[4],gridc[5],gridc[6],gridc[7])

		# For the empty positions check for any moves - only for 'O's in case of against AI
		indx = 0
		for i in range(3):
			for j in range(3):
				if board[i][j] == '_':
					if ((containsCircle(grids[indx]))):
						board[i][j] = PLAYER
						print(i,j)
						print(board)
						print('Move Detected')
						return [(i,j),True]
				indx+=1

		#print('No Move Detected')
		return [(),False]
		
	def blockingOverlay(self, text, time=3):
		# updat the global variable
		global OVERLAY_TEXT

		OVERLAY_TEXT = text
		QtTest.QTest.qWait(time*1000)
		OVERLAY_TEXT = ''

		


	def connectToGameRoom(self):
		global test_client, join_status

		if join_status == 0:
			# Get connection details
			username = self.uname_edit.text()
			server = self.server_edit.text()
			port = (int)(self.port_edit.text())

			# Establish Connection
			addr = (server,port)
			client = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
			client.connect(addr)

			self.global_client = client

			# test the global client
			test_client = client

			# Make changes to UI accordingly
			join_status = 1
			self.uname_edit.setEnabled(False)
			self.server_edit.setEnabled(False)
			self.port_edit.setEnabled(False)

			self.join_btn.setText("Leave")

			print(username,server,port)

			# send the username to the server
			client.send(username.encode(FORMAT))

			# lets start a thread to continously listen to server
			self.thread = ExecuteThread()
			self.thread.start()
			self.thread.my_signal.connect(self.messageBox)

			# Connect to the Game Look
			self.connectToNetworkGame()

		else:
			
			join_status = 0
			self.uname_edit.setEnabled(True)
			self.server_edit.setEnabled(True)
			self.port_edit.setEnabled(True)

			self.join_btn.setText("Join")

			self.closeConn()

	def messageBox(self,msg):
		global TURN, PLAYER, OPPONENT, GAME_STATUS, board, OPPONENT_MOVED

		# If the received message is DISCONNECT_MSG then exit
		if(msg == DISCONNECT_MSG):
			closeConn(test_client)

		elif(msg.split()[0] == 'player:'):
			if msg.split()[1] == 'x':
				TURN = 1
				PLAYER = 'x'
				OPPONENT = 'o'
			else:
				TURN = 0
				PLAYER = 'o'
				OPPONENT = 'x'

			GAME_STATUS = 1
			print('active game')

		elif(msg.split()[0] == 'move:'):
			i = (int)(msg.split()[1])
			j = (int)(msg.split()[2])
			board[i][j] = OPPONENT
			OPPONENT_MOVED = 1

	def sendMessage(self, msg):		
		# Send the msg to the server to be broadcasted
		self.global_client.send(msg.encode(FORMAT))

	def closeConn(self):
		global test_client

		print("close")
		test_client.send(DISCONNECT_MSG.encode(FORMAT))
		self.lineEdit.setEnabled(False)
		self.pushButton.setEnabled(False)
		time.sleep(1)
		sys.exit()

	def connectToCamera(self):

		global CAM_STATE

		# Get the camera ip address
		cam_ip = self.cam_ip_edit.text()

		# change state of button and edit
		if CAM_STATE == 0:
			self.cam_connect_btn.setText("Disconnect")
			self.cam_ip_edit.setEnabled(False)

			# Establish connection to the ip cam
			self.camWorker = camWorker(cam_ip)
			self.camWorker.start()
			self.camWorker.imageUpdate.connect(self.imageUpdateSlot)

			# overlay
			self.blockingOverlay('Camera Connected')

			CAM_STATE = 1

		else:
			self.camWorker.stop()
			self.cam_connect_btn.setText("Connect")
			self.cam_ip_edit.setEnabled(True)

			CAM_STATE = 0

	def imageUpdateSlot(self, img):
		self.img = img
		self.camera_label.setPixmap(QPixmap.fromImage(img))

   
class camWorker(QThread):
	imageUpdate = pyqtSignal(QImage)

	def __init__(self,ipaddr):
		super().__init__()
		self.ipaddr = ipaddr

	def run(self):

		global board_img, GAME_STATUS, PLAY_MODE, OVERLAY_TEXT

		self.threadActive = True

		if self.ipaddr == '0' or self.ipaddr == '':
			cap = cv2.VideoCapture(0)
		else:
			cam_url = "https://"+self.ipaddr+"/video"
			cap = cv2.VideoCapture(cam_url)

		while self.threadActive:
			ret, frame = cap.read()
			if ret:
				img = cv2.resize(frame, (900,500))
				board_img = img	
				if OVERLAY_TEXT != '':
					if OVERLAY_TEXT == 'Camera Connected':
						img_grid = cv2.putText(img, OVERLAY_TEXT, (40,250), cv2.FONT_HERSHEY_PLAIN, 5, (0, 255, 0), 5, cv2.LINE_AA)
					else:
						img_grid = cv2.putText(img, OVERLAY_TEXT, (200,250), cv2.FONT_HERSHEY_PLAIN, 5, (0, 255, 0), 5, cv2.LINE_AA)
				else:
					img_grid = getGrids(img)
					#img_grid = cv2.resize(img_grid, (900,500))

				# overlay images if necessary
				if GAME_STATUS == 1 and OVERLAY_TEXT == '':
					self.overlayOppMoves(img_grid)

				img = cv2.cvtColor(img_grid,cv2.COLOR_BGR2RGB)
				img = cv2.resize(img, (900,500))
				imgQFormat = QImage(img.data, img.shape[1], img.shape[0], QImage.Format_RGB888)
				pic = imgQFormat.scaled(900,500, Qt.KeepAspectRatio)
				self.imageUpdate.emit(pic)
				QtTest.QTest.qWait(100)

	def overlayOppMoves(self,img):
		global board, grid_coordinates, OPPONENT
		indx = 0
		for i in range(3):
			for j in range(3):
				if board[i][j] == OPPONENT:
					pos = self.getGridPos(indx+1,grid_coordinates)
					cv2.putText(img, OPPONENT, pos, cv2.FONT_HERSHEY_PLAIN, 10, (0, 0, 255), 5, cv2.LINE_AA)
				indx+=1
	
	def getGridPos(self,indx,gridc):

		h1, h2, v1, v2, p1, p2, p3, p4 = gridc

		#print(indx)

		if indx == 1:
			#print('playerd')
			return (h1[0][0]+10,p1[1]-130)

		elif indx == 2:
			return (p1[0]+50,p1[1]-80)

		elif indx == 3:
			return (p2[0]+30,p2[1]-70)

		elif indx == 4:
			return (h2[0][0]+10,p1[1]+70)

		elif indx == 5:
			return (p1[0]+70,p1[1]+150)

		elif indx == 6:
			return (p2[0]+20,p2[1]+120)

		elif indx == 7:
			return (h2[0][0]+10,p4[1]+140)

		elif indx == 8:
			return (p1[0]+20,p4[1]+40)

		else:
			return (p2[0]+40,p4[1]+40)

	def stop(self):
		self.threadActive = False
		self.quit()

class ExecuteThread(QThread):
	my_signal = pyqtSignal(str)
	global TURN, PLAYER, OPPONENT, GAME_STATUS, board

	def run(self):
		while 1:
			# recevie message
			msg = test_client.recv(4096).decode(FORMAT)

			# emit signal
			self.my_signal.emit(msg)

			#print(msg)

class OverlayThread(QThread):

	def __init__(self,message):
		super().__init__()
		self.msg = message

	def run(self):
		global board_img
		time.sleep(2)
		print(board_img)
		pos = (board_img.shape[1]//2,board_img.shape[0]//2)

		while 1:
			cv2.putText(board_img, self.msg, pos, cv2.FONT_HERSHEY_PLAIN, 10, (0, 0, 255), 5, cv2.LINE_AA)

	def stop(self):
		self.quit()


if __name__ == "__main__":
	import sys
	app = QtWidgets.QApplication(sys.argv)
	w = MainWindow()
	w.show()
	sys.exit(app.exec_())