import numpy as np
import argparse
import cv2

def parse_args():

	parser = argparse.ArgumentParser(
		description=__doc__,
		formatter_class=argparse.RawDescriptionHelpFormatter)

	parser.add_argument("-i", "--image", help = "path to the image file")
	parser.add_argument("-c", "--coords", help = "comma seperated list of source points")

	return parser.parse_args()

def main():
	# construct the argument parse and parse the arguments

	args = parse_args()

	img = args.image
	image = cv2.imread(img)

	coords = args.coords
	pts = np.array(eval(coords), dtype = "float32")
	print("coordinates: ", coords)

	warped = four_point_transform(image, pts)

def order_points(pts):
	rect = np.zeros((4, 2), dtype = "float32")
 
	# top left, bottom right
	s = pts.sum(axis = 1)
	rect[0] = pts[np.argmin(s)]
	rect[2] = pts[np.argmax(s)]
 
	#top right, bottom left
	diff = np.diff(pts, axis = 1)
	rect[1] = pts[np.argmin(diff)]
	rect[3] = pts[np.argmax(diff)]
 
	# return the ordered coordinates
	return rect

def four_point_transform(image, pts):
	# obtain a consistent order of the points and unpack them

	rect = order_points(pts)
	(tl, tr, br, bl) = rect
 
	widthA = np.sqrt(((br[0] - bl[0]) ** 2) + ((br[1] - bl[1]) ** 2))
	widthB = np.sqrt(((tr[0] - tl[0]) ** 2) + ((tr[1] - tl[1]) ** 2))
	maxWidth = max(int(widthA), int(widthB))
 
	heightA = np.sqrt(((tr[0] - br[0]) ** 2) + ((tr[1] - br[1]) ** 2))
	heightB = np.sqrt(((tl[0] - bl[0]) ** 2) + ((tl[1] - bl[1]) ** 2))
	maxHeight = max(int(heightA), int(heightB))
 
	dst = np.array([
		[0, 0],
		[maxWidth - 1, 0],
		[maxWidth - 1, maxHeight - 1],
		[0, maxHeight - 1]], dtype = "float32")
 
	# compute the perspective transform matrix and then apply it
	M = cv2.getPerspectiveTransform(rect, dst)
	warped = cv2.warpPerspective(image, M, (maxWidth, maxHeight))
 
	# return the warped image
	return warped

if __name__ == '__main__':
    main()