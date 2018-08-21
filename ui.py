import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import numpy as np
import rescale
import laser_pipeline
from matplotlib.widgets import Slider, Button
import cv2


phase = 0
coordinates = []
img = mpimg.imread("toolssmall.png")

paper_width = 17.0
paper_height = 11.0


#global state
warped = None
black_white = None
dilated = None
paths = None
smooth = None
w = None
h = None
cleanup_number = 100

# Build ui
fig, ax = plt.subplots(nrows=2, ncols=1, figsize =(7,7), gridspec_kw = {'height_ratios':[1, .05]})
image_axes = ax[0]
image_axes.imshow(img)

if(phase == 0):
	image_axes.text(200,-25,"Phase 1: Fixing Image Distortion", fontsize=12, horizontalalignment='center',
			verticalalignment='center')
	plt.title(" ")

# axthreshold = plt.axes([0.25, 0.15, 0.65, 0.03], facecolor='salmon')
axthreshold = ax[1]
threshold_slider = Slider(axthreshold, ' ', 0, 100, valfmt='%0.0f')

#Creates slider and button
axnext = plt.axes([0.81, 0.02, 0.1, 0.05])
bnext = Button(axnext, 'Next')

def draw_paths(smooth, cleanup_number, image_axes):
	for path in smooth:
			if len(path) < cleanup_number:
				continue
			x_coordinate = []
			y_coordinate = []

			for p in path:
				x_coordinate.append(p[0])
				y_coordinate.append(p[1])
			image_axes.plot(x_coordinate, y_coordinate, 'c-')

#callback funcs
#*************************************************************************************************************************************
# Fixing Image Distortion

def onclick(event):
	global phase
	global warped

	if phase != 0:
		return

	if event.inaxes != image_axes:
		return

	x_coordinate = event.xdata
	y_coordinate = event.ydata

	coordinates.append([x_coordinate, y_coordinate])	
	image_axes.plot(x_coordinate, y_coordinate, 'c*')

	fig.canvas.draw()

	if (len(coordinates) == 4):
		tmp = np.array(coordinates)
		image_axes.cla()

		warped = rescale.four_point_transform(img, tmp)
		image_axes.imshow(warped)
		fig.canvas.draw_idle()

		update(threshold_slider.val)

		image_axes.text(150,-25,"Phase 2: Conversion to Black and White", fontsize=12, horizontalalignment='center',
			verticalalignment='center')

		phase = 1

#*************************************************************************************************************************************
# SLIDER

def update(val):
	global phase
	global warped
	global black_white
	global dilated
	global paths
	global smooth 
	global w
	global h 
	global cleanup_number

	to_show = black_white

	if phase == 0:
		return

	if phase == 6:
		return

	image_axes.cla()

	#*******************************************************************************
	# Black and White 

	if phase == 1:
		# threshold_slider.valstep = 1
		# threshold_slider.valmax = 50

		threshold_slider.label = "Threshold for B&W"
		threshold = threshold_slider.val/threshold_slider.valmax

		w = warped.shape[0]
		h = warped.shape[1]

		black_white = laser_pipeline.make_grayscale(warped, w, h, threshold)
		to_show = black_white

		image_axes.text(150,-25,"Phase 2: Conversion to Black and White", fontsize=12, horizontalalignment='center',
		verticalalignment='center')

	#*******************************************************************************
	# Dilation

	if phase == 2:
		# threshold_slider.valmax = 40

		dilation_number = int(threshold_slider.val/threshold_slider.valmax*10)
		dilated = laser_pipeline.dilate(black_white, dilation_number)
		to_show = dilated
	
		image_axes.text(80,-25,"Phase 3: Dilation", fontsize=12, horizontalalignment='center',
		verticalalignment='center')

	#*******************************************************************************
	# Cleaning Out Paths 

	if phase == 3:
		cleanup_number = 100 + int(threshold_slider.val/threshold_slider.valmax*400)
		draw_paths(paths, cleanup_number, image_axes)

		to_show = dilated
		
	#*******************************************************************************
	# Smoothing

	if phase == 4:
		threshold_slider.valmin = 6

		smooth_number = int(threshold_slider.val/threshold_slider.valmax*20)
		smooth = laser_pipeline.smooth_path(smooth_number, paths)
		draw_paths(smooth, cleanup_number, image_axes)

		to_show = warped

	#*******************************************************************************
	# Creating SVG

	if phase == 5:
		to_show = warped
		#laser_pipeline.create_svg(name, cleanup_number, smooth, w, h, x_p2i, y_p2i)

	#*************************************************************************************

	image_axes.imshow(to_show)
	fig.canvas.draw_idle()

#*******************************************************************************************************************************

def reset(threshold_slider):
	if(threshold_slider.val != threshold_slider.valinit):
		threshold_slider.set_val(threshold_slider.valinit)

#*******************************************************************************************************************************
# BUTTON

def next(event):
	global phase
	global black_white
	global warped
	global dilated
	global paths
	global smooth
	global w
	global h 
	global cleanup_number
	global paper_width
	global paper_height

	phase = phase + 1
	
	#********************************************************************************
	# Dilation

	if phase == 2:
		if black_white is None:
			phase = phase - 1
			return
		dilated = laser_pipeline.dilate(black_white, 1)

		image_axes.cla()
		image_axes.imshow(dilated)
		fig.canvas.draw_idle()

		reset(threshold_slider)

		image_axes.text(80,-25,"Phase 3: Dilation", fontsize=12, horizontalalignment='center',
		verticalalignment='center')

	#********************************************************************************
	# Clean Up

	if phase == 3:
		w = black_white.shape[0]
		h = black_white.shape[1]

		paths = laser_pipeline.line_segment(dilated, w, h)

		image_axes.cla()
		image_axes.imshow(dilated)
		fig.canvas.draw_idle()
		reset(threshold_slider)

		draw_paths(paths, cleanup_number, image_axes)

		image_axes.text(80,-25,"Phase 4: Clean Up", fontsize=12, horizontalalignment='center',
		verticalalignment='center')

	#*******************************************************************************
	# Smoothing

	if phase == 4:

		threshold_slider.valmin = 6

		smooth_number = 1
		smooth = laser_pipeline.smooth_path(smooth_number, paths)
		
		image_axes.cla()
		image_axes.imshow(warped)

		draw_paths(smooth, cleanup_number, image_axes)

		image_axes.text(80,-25,"Phase 5: Smoothing", fontsize=12, horizontalalignment='center',
		verticalalignment='center')
	#************************************************************************************************
	# Creating SVG

	if phase == 5:
		w = black_white.shape[0]
		h = black_white.shape[1]

		x_p2i = paper_width/h
		y_p2i = paper_height/w

		name = "outline.svg"
		laser_pipeline.create_svg(name, cleanup_number, smooth, h, w, x_p2i, y_p2i)

		plt.title("Done", color = "r", fontsize = 10, fontweight="bold")
	#************************************************************************************************

	fig.canvas.draw_idle()

# Connect callbacks
cid = fig.canvas.mpl_connect('button_press_event', onclick)
threshold_slider.on_changed(update)
bnext.on_clicked(next)
plt.show()