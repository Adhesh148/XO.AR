import numpy as np
import math
import cv2

def getGridPts(img):
	"""
	returns the coordinate points of the 9 grids to be detected
	:param img: raw src image
	"""
	
	# Step-1: Preprocess the raw img
	img_resized = cv2.resize(img,(800,800), interpolation = cv2.INTER_AREA)
	#img_bright = shadowRemoval(img_resized)
	img_gray = cv2.cvtColor(img_resized,cv2.COLOR_BGR2GRAY)
	img_blur = cv2.GaussianBlur(img_gray,(5,5),3)
	img_canny = cv2.Canny(img_blur,50,50)
	
	# Step-2: Detect lines in the image
	
	# Parameters of Houglines function
	rho = 1                                  # distance resolution in pixels of the Hough grid
	theta = np.pi / 200                      # angular resolution in radians of the Hough grid
	threshold = 70                           # minimum number of votes (intersections in Hough grid cell)
	min_line_length = 50                     # minimum number of pixels making up a line
	max_line_gap = 100                       # maximum gap in pixels between connectable line segments
	line_image = np.copy(img_resized) * 0    # creating a blank to draw lines on

	# Run Hough on edge detected image
	lines = cv2.HoughLinesP(img_canny, rho, theta, threshold, np.array([]),
						min_line_length, max_line_gap)
	
	# separate the coordinates into separate lists
	if lines.size == 0:
		return img_resized, []

	flat_lines_lst = lines.flatten()
	num_lines = len(flat_lines_lst)
	start_x, start_y, end_x, end_y = flat_lines_lst[::4], flat_lines_lst[list(range(1,num_lines,4))], \
										flat_lines_lst[list(range(2,num_lines,4))], flat_lines_lst[list(range(3,num_lines,4))]
	
	# Get important coordinates related to the grid
	xmin_indx = np.argmin(start_x)
	xmax_indx = np.argmax(end_x)
	ymin_indx = np.argmin(start_y)
	ymax_indx = np.argmax(end_y)
	
	# Get the coordinates of the horizontal lines
	H1 = [(start_x[xmin_indx],start_y[xmin_indx]),(end_x[xmax_indx],start_y[xmin_indx])]      # first Hline
	
	# The second horizontal line differs from H1 only in its y axis
	y2 = 0
	next_min_indx = xmin_indx
	temp_start_x = start_x.copy()
	while(True):
		temp_start_x[next_min_indx] = 10000
		next_min_indx = np.argmin(temp_start_x)
		if(np.abs(start_y[next_min_indx] - H1[0][1]) > 200):
			y2 = start_y[next_min_indx]
			break
	
	H2 = [(start_x[xmin_indx],y2),(end_x[xmax_indx],y2)]
	
	# Get the coordinates of the vertical lines
	V1 = [(start_x[ymin_indx], start_y[ymin_indx]), (start_x[ymin_indx],end_y[ymax_indx])]
	
	# Find x axis of the V2 line
	x2 = 0
	next_min_indx = ymin_indx
	temp_start_y = start_y.copy()
	while(True):
		temp_start_y[next_min_indx] = 10000
		next_min_indx = np.argmin(temp_start_y)
		if(np.abs(start_x[next_min_indx] - V1[0][0]) > 200):
			x2 = start_x[next_min_indx]
			break
	
	V2 = [(x2,V1[0][1]), (x2,V1[1][1])]
	
	# Find the intersection points
	P1 = (V1[0][0],H1[0][1])
	P2 = (V2[0][0],H1[0][1])
	P3 = (V1[0][0],H2[0][1])
	P4 = (V2[0][0],H2[0][1])
	
	"""
	img_final = img_resized.copy()
	cv2.circle(img_final, H1[0], radius=5, color=(0, 0, 255), thickness=5)
	cv2.circle(img_final, H1[1], radius=5, color=(0, 0, 255), thickness=5)
	cv2.circle(img_final, H2[0], radius=5, color=(0, 0, 255), thickness=5)
	cv2.circle(img_final, H2[1], radius=5, color=(0, 0, 255), thickness=5)
	cv2.circle(img_final, V1[0], radius=5, color=(0, 0, 255), thickness=5)
	cv2.circle(img_final, V1[1], radius=5, color=(0, 0, 255), thickness=5)
	cv2.circle(img_final, V2[0], radius=5, color=(0, 0, 255), thickness=5)
	cv2.circle(img_final, V2[1], radius=5, color=(0, 0, 255), thickness=5)
	
	cv2.circle(img_final, P1, radius=5, color=(0, 0, 255), thickness=5)
	cv2.circle(img_final, P2, radius=5, color=(0, 0, 255), thickness=5)
	cv2.circle(img_final, P3, radius=5, color=(0, 0, 255), thickness=5)
	cv2.circle(img_final, P4, radius=5, color=(0, 0, 255), thickness=5)
	"""
	
	# Get the relevant vertices in order
	if H1[0][1] < H2[0][1]:
		h1 = H1
		h2 = H2
	else:
		h1 = H2
		h2 = H1
		
	if V1[0][0] < V2[0][0]:
		v1 = V1
		v2 = V2
	else:
		v1 = V2
		v2 = V1
		
	p1 = (v1[0][0],h1[0][1])
	p2 = (v2[0][0],h1[0][1])
	p3 = (v2[0][0],h2[0][1])
	p4 = (v1[0][0],h2[0][1])
	
	coordinates = [h1,h2,v1,v2,p1,p2,p3,p4]
	
	return coordinates

def getGridImage(img, h1, h2, v1, v2, p1, p2, p3, p4):

	img_resized = cv2.resize(img,(800,800), interpolation = cv2.INTER_AREA)

	# Get all the nine grids
	grid1 = img_resized[max(v1[0][1]-50,0):p1[1]-5,max(h2[0][0]-100,0):p1[0]-10]
	grid2 = img_resized[max(v1[0][1]-50,0):p1[1]-5,p1[0]+5:p2[0]-10]
	grid3 = img_resized[max(v1[0][1]-50,0):p1[1]-5,p2[0]+5:h1[1][0] + 100]
	
	grid4 = img_resized[p1[1]+10:p4[1]-10,max(h2[0][0]-100,0):p1[0]-10]
	grid5 = img_resized[p1[1]+10:p4[1]-10,p1[0]+5:p2[0]-10]
	grid6 = img_resized[p1[1]+10:p4[1]-100,p2[0]+5:h1[1][0] + 10]
	
	grid7 = img_resized[p4[1]+10:v1[1][1]+50,max(h2[0][0]-100,0):p1[0]-10]
	grid8 = img_resized[p4[1]+10:v1[1][1]+50,p1[0]+5:p2[0]-10]
	grid9 = img_resized[p4[1]+10:v1[1][1]+50,p2[0]+5:h1[1][0] + 70]
	
	grids = [grid1, grid2, grid3, grid4, grid5, grid6, grid7, grid8, grid9]

	return grids


def containsCross(img):
	"""
	returns True if grid has cross ; else 0
	"""

	imgGray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
	template = cv2.imread('template.jpg',0)

	res = cv2.matchTemplate(imgGray,template,cv2.TM_CCOEFF_NORMED)

	# Specify a threshold
	threshold = 0.4

	# Store the coordinates of matched area in a numpy array
	loc = np.where( res >= threshold)

	if loc[0].size == 0:
		return False
	return True

def isGridFilled(grid):
	"""
	returns True if grid is filled with either X or O; else False
	"""
	imgRsize = cv2.resize(grid,(200,200), interpolation = cv2.INTER_AREA)
	imgGray = cv2.cvtColor(imgRsize,cv2.COLOR_BGR2GRAY)
	imgBlur = cv2.GaussianBlur(imgGray,(5,5),3)
	imgCanny = cv2.Canny(imgBlur,50,50)

	num_wt_pixels = np.sum(imgCanny == 255)
	#print(num_wt_pixels)
	if num_wt_pixels/(200*200) > 0.4:
		return True

	else:
		return False

def containsCircle(img):
	"""
	returns True if grid has circle; else 0
	"""
	imgRsize = cv2.resize(img,(200,200), interpolation = cv2.INTER_AREA)
	imgGray = cv2.cvtColor(imgRsize,cv2.COLOR_BGR2GRAY)
	imgBlur = cv2.GaussianBlur(imgGray,(5,5),3)
	#imgCanny = cv2.Canny(imgBlur,50,50)
	
	detected_circles = cv2.HoughCircles(imgBlur, 
				   cv2.HOUGH_GRADIENT, 1, 20, param1 = 50,
			   param2 = 30, minRadius = 1, maxRadius = 40)
	
	if detected_circles is not None:
		return True
	else:
		return False

def getGrids(img):
	"""
	returns the coordinate points of the 9 grids to be detected
	:param img: raw src image
	"""
	
	# Step-1: Preprocess the raw img
	img_resized = cv2.resize(img,(800,800), interpolation = cv2.INTER_AREA)
	#img_bright = shadowRemoval(img_resized)
	img_gray = cv2.cvtColor(img_resized,cv2.COLOR_BGR2GRAY)
	img_blur = cv2.GaussianBlur(img_gray,(5,5),3)
	img_canny = cv2.Canny(img_blur,50,50)
	
	# Step-2: Detect lines in the image
	
	# Parameters of Houglines function
	rho = 1                                  # distance resolution in pixels of the Hough grid
	theta = np.pi / 200                      # angular resolution in radians of the Hough grid
	threshold = 70                           # minimum number of votes (intersections in Hough grid cell)
	min_line_length = 50                     # minimum number of pixels making up a line
	max_line_gap = 100                       # maximum gap in pixels between connectable line segments
	line_image = np.copy(img_resized) * 0    # creating a blank to draw lines on

	# Run Hough on edge detected image
	lines = cv2.HoughLinesP(img_canny, rho, theta, threshold, np.array([]),
						min_line_length, max_line_gap)
	
	# separate the coordinates into separate lists
	if lines.size == 0:
		return img_resized, []

	flat_lines_lst = lines.flatten()
	num_lines = len(flat_lines_lst)
	start_x, start_y, end_x, end_y = flat_lines_lst[::4], flat_lines_lst[list(range(1,num_lines,4))], \
										flat_lines_lst[list(range(2,num_lines,4))], flat_lines_lst[list(range(3,num_lines,4))]
	
	# Get important coordinates related to the grid
	xmin_indx = np.argmin(start_x)
	xmax_indx = np.argmax(end_x)
	ymin_indx = np.argmin(start_y)
	ymax_indx = np.argmax(end_y)
	
	# Get the coordinates of the horizontal lines
	H1 = [(start_x[xmin_indx],start_y[xmin_indx]),(end_x[xmax_indx],start_y[xmin_indx])]      # first Hline
	
	# The second horizontal line differs from H1 only in its y axis
	y2 = 0
	next_min_indx = xmin_indx
	temp_start_x = start_x.copy()
	while(True):
		temp_start_x[next_min_indx] = 10000
		next_min_indx = np.argmin(temp_start_x)
		if(np.abs(start_y[next_min_indx] - H1[0][1]) > 200):
			y2 = start_y[next_min_indx]
			break
	
	H2 = [(start_x[xmin_indx],y2),(end_x[xmax_indx],y2)]
	
	# Get the coordinates of the vertical lines
	V1 = [(start_x[ymin_indx], start_y[ymin_indx]), (start_x[ymin_indx],end_y[ymax_indx])]
	
	# Find x axis of the V2 line
	x2 = 0
	next_min_indx = ymin_indx
	temp_start_y = start_y.copy()
	while(True):
		temp_start_y[next_min_indx] = 10000
		next_min_indx = np.argmin(temp_start_y)
		if(np.abs(start_x[next_min_indx] - V1[0][0]) > 200):
			x2 = start_x[next_min_indx]
			break
	
	V2 = [(x2,V1[0][1]), (x2,V1[1][1])]
	
	# Find the intersection points
	P1 = (V1[0][0],H1[0][1])
	P2 = (V2[0][0],H1[0][1])
	P3 = (V1[0][0],H2[0][1])
	P4 = (V2[0][0],H2[0][1])
	
	
	img_final = img_resized.copy()
	cv2.circle(img_final, H1[0], radius=5, color=(0, 0, 255), thickness=5)
	cv2.circle(img_final, H1[1], radius=5, color=(0, 0, 255), thickness=5)
	cv2.circle(img_final, H2[0], radius=5, color=(0, 0, 255), thickness=5)
	cv2.circle(img_final, H2[1], radius=5, color=(0, 0, 255), thickness=5)
	cv2.circle(img_final, V1[0], radius=5, color=(0, 0, 255), thickness=5)
	cv2.circle(img_final, V1[1], radius=5, color=(0, 0, 255), thickness=5)
	cv2.circle(img_final, V2[0], radius=5, color=(0, 0, 255), thickness=5)
	cv2.circle(img_final, V2[1], radius=5, color=(0, 0, 255), thickness=5)
	
	cv2.circle(img_final, P1, radius=5, color=(0, 0, 255), thickness=5)
	cv2.circle(img_final, P2, radius=5, color=(0, 0, 255), thickness=5)
	cv2.circle(img_final, P3, radius=5, color=(0, 0, 255), thickness=5)
	cv2.circle(img_final, P4, radius=5, color=(0, 0, 255), thickness=5)
	
	return img_final