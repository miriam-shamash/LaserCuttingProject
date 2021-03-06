# Laser Cutting Project - GSTEM 2018

We propose a method to efficiently and robustly create a case to secure an object in place. This method can be used for producing environmentally-friendly shipping containers to hold objects securely during transport, or to create tool-holders to maximize organization and decrease clutter in a workspace. 

To achieve this goal, we propose an automated pipeline to convert a raster image of the desired layout, acquired by a commodity camera, into a set of toolpaths for a laser cutter. The image is processed by eliminating perspective distortion, thresholded and dilated to extract the outlines of the objects, and finally converted into a vector graphics file. A laser cutter can then produce cardboard sheets that, when stacked on top of one another, realize the tool holder. This algorithm produces a holder to hold any object securely, regardless of shape. We demonstrate the practical applicability of our algorithm on a set of challenging test cases, and we release our reference implementation as an open-source project to foster adoption of our technique.

[Video](Video.mp4)

[Detailed Description](Report.pdf)

Slides ([1](Slides.zip) [2](Slides.z01))
