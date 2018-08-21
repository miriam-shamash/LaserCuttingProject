import argparse
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import numpy as np
import svgwrite
import math
import cv2

def parse_args():

	parser = argparse.ArgumentParser(
		description=__doc__,
		formatter_class=argparse.RawDescriptionHelpFormatter)
	
	parser.add_argument("image", type=str, help="the input image")
	parser.add_argument("--threshold", "-t", type=float, default=0.5, help="threshold for the detection of obj")
	parser.add_argument("--blackwhite", "-bw", type=str, default=None, help="name of image")
	parser.add_argument("--x_pixel_to_inches", "-x_p2i", type=float, default=4, help="")
	parser.add_argument("--y_pixel_to_inches", "-y_p2i", type=float, default=4, help="")

	parser.add_argument("--clean_path", "-cp", type=float, default=200, help="")
	parser.add_argument("--smooth_number", "-sn", type=int, default=2, help="")
	#parser.add_argument("--name", "-n", type=str, default="polygon", help="")

	return parser.parse_args()

#********************************************************************************************

def main():
	args = parse_args() 
   
	img = mpimg.imread(args.image)
	threshold = args.threshold

	w = img.shape[0]
	h = img.shape[1]

	img = make_grayscale(img,w,h, threshold)
	plt.imshow(img)

	if args.blackwhite is not None:
		image = plt.imshow(img)
		save(image)

	x_p2i = args.x_pixel_to_inches
	y_p2i = args.y_pixel_to_inches

	paths = line_segment(img,w, h)

	smooth_number = args.smooth_number
	new_paths = smooth_path(smooth_number,paths)

	name = "polygon.svg"
	clean_path = args.clean_path
	create_svg(name, clean_path, new_paths, w, h, x_p2i, y_p2i)

#********************************************************************************************
# Converts the image to greyscale then black and white

def make_grayscale(img, w, h, threshold):
	result = np.zeros((w, h, 3))
	for i in range(0, w):
		for j in range(0, h):
			
			r = img[i,j, 0] 
			g = img[i,j, 1]
			b = img[i,j, 2]

			average = (r+g+b)/3.0
			# print(average)
			
			#Changes grayscale to black and white 
			if average > threshold:
				average = 1.0
			else:
				average = 0.0

			#print(average)
			result[i,j, 0] = average
			result[i,j, 1] = average 
			result[i,j, 2] = average

	return result  

#********************************************************************************************
# Dilates the image

def dilate(black_white, dilation_number):
	tmp = np.zeros([black_white.shape[0], black_white.shape[1]], dtype=np.uint8)
	for i in range(black_white.shape[0]):
		for j in range(black_white.shape[1]):
			tmp[i, j] = 255 - black_white[i, j, 0]*255
	

	kernel = np.ones((5,5), np.uint8)
	tmp = cv2.dilate(tmp, kernel, iterations = dilation_number)
	dilated = np.zeros([tmp.shape[0], tmp.shape[1], 3])
	
	for i in range(dilated.shape[0]):
		for j in range(dilated.shape[1]):
			dilated[i, j, 0] = dilated[i, j, 1] = dilated[i, j, 2] = (255 - tmp[i, j])/255

	return dilated

#********************************************************************************************
# Saves the image

def save(image):
	plt.axis('off')
	image.axes.get_xaxis().set_visible(False)
	image.axes.get_yaxis().set_visible(False)

	#Saves the image
	plt.savefig('blackAndWhite.png', bbox_inches='tight', pad_inches = 0)

#********************************************************************************************
# Creates a list of line segments and merges them into a single path

def line_segment(img, w, h):

	paths = []

	edges = []
	for i in range(1,w):
		for j in range(1,h):

			#Array of all the surrounding values of the point
			y = np.array([img[i-1,j, 0], img[i,j-1, 0]])#, img[i,j+1, 0], img[i+1,j, 0]])

			#Loops through the values of the second array 
			for k in range (0,2):
					if img[i,j, 0] != y[k]:
						
						# k = 0 top
						# k = 1 left
						# k = 2 right
						# k = 3 bottom  
						
						z = np.array([[j,i], [j+1,i], [j,i+1]]) #[j+1,i+1]])
						#print(z)

						if(k==0):
							firstPoint = int(z[0,0]), int(z[0,1])
							endPoint = int(z[1,0]), int(z[1,1])

						elif(k==1):
							firstPoint = int(z[0,0]), int(z[0,1])
							endPoint = int(z[2,0]), int(z[2,1])

						# elif(k==2):
						#     firstPoint = int(z[1,0]), int(z[1,1])
						#     endPoint = int(z[3,0]), int(z[3,1])

						# elif(k==3):
						#     firstPoint = int(z[2,0]), int(z[2,1])
						#     endPoint = int(z[3,0]), int(z[3,1])
						   
						edges.append((firstPoint, endPoint))                        

	visited = []

	for i in range(len(edges)):
		#print(len(edges))
		visited.append(False)

	while True:
		path = []
		
		notAllVisited = False
		for index in range(len(edges)):
			if not visited[index]:
				notAllVisited = True
				break

		if not notAllVisited:
			break

		#Adds the first edge to the path
		path.append(edges[index][0])
		path.append(edges[index][1])

		visited[index] = True

		stop = False
		triedReversed = False

		while not stop:
			hasFoundOne = False
			for i in range(len(edges)):
				e = edges[i]

				if visited[i]:
					continue

				current_v = path[len(path) - 1]

				if(distance(current_v,e[0]) < 1e-8):
					if(distance(e[1], path[0]) < 1e-8):
						stop = True
					
					path.append(e[1])
					visited[i] = True
					hasFoundOne = True
					break

				elif(distance(current_v, e[1]) < 1e-8):
					if(distance(e[0], path[0]) < 1e-8):
						stop = True

					path.append(e[0])
					visited[i] = True
					hasFoundOne = True
					break

			if not hasFoundOne:
				if triedReversed:
					break
				else:
					path.reverse()
					triedReversed = True
				
		paths.append(path)

	return paths

#********************************************************************************************
# Computes the distance between two points

def distance(p1,p2):
	dx = p2[0] - p1[0]
	dy = p2[1] - p1[1]

	distance = math.sqrt(dx**2 + dy**2)
	return distance

#********************************************************************************************
# Smooths the path

def smooth_path(smooth_number, paths):
	
	for i in range(smooth_number):
		new_paths = []

		for j in range(len(paths)):
			#gets the path in order
			old_path = paths[j]

			new_path = []

			for k in range(len(old_path)):
				if k == 0:
					new_path.append(old_path[0])

				elif k == len(old_path)-1:
					new_path.append(old_path[k])

				else:
					averageX = (old_path[k-1][0] + old_path[k+1][0])/2
					averageY = (old_path[k-1][1] + old_path[k+1][1])/2
					new_path.append([averageX, averageY])

			new_paths.append(new_path)
		paths = new_paths

	return new_paths

#********************************************************************************************
# Creates the SVG and scale it

def create_svg(name, clean_path, new_paths, w, h, x_p2i, y_p2i):
	dwg = svgwrite.Drawing(name, size = (str(w*x_p2i) + "in", str(h*y_p2i) + "in"), viewBox = (0, 0, 17, 11), debug=True)

	lines = dwg.add(dwg.g(stroke_width = "0.001in", stroke='black', fill='none'))
	
	#Cleans out the small paths
	for new_path in new_paths:
		if len(new_path) < clean_path:
			continue

		tmp = []
		for p in new_path:
			tmp.append([p[0]*x_p2i, p[1]*y_p2i])
			# print(p[0], p[1])
			# print(w, h)
			# print(x_p2i, y_p2i)
			# asd

		lines.add(dwg.polyline(tmp))
	dwg.save()
	return dwg

#********************************************************************************************

if __name__ == '__main__':
	main()