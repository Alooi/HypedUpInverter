
# import the modules
import sys, getopt
import os
from os import listdir
import numpy as np
import cv2
 
def mse(pathA, pathB):
	imageA = cv2.imread(pathA)
	imageB = cv2.imread(pathB)
	# the 'Mean Squared Error' between the two images is the
	# sum of the squared difference between the two images;
	# NOTE: the two images must have the same dimension
	err = np.sum((imageA.astype("float") - imageB.astype("float")) ** 2)
	err /= float(imageA.shape[0] * imageA.shape[1])
	
	# return the MSE, the lower the error, the more "similar"
	# the two images are
	return err

def mse_average(gt, gn):
	# get the path/directory
	for images in os.listdir(gt):
		print(mse(gt +"/"+images, gn +"/"+images))


def main(argv):
   gt = ''
   gn = ''
   try:
      opts, args = getopt.getopt(argv,"hi:o:",["ifile=","ofile="])
   except getopt.GetoptError:
      print ('test.py -i <gt> -o <gn>')
      sys.exit(2)
   for opt, arg in opts:
      if opt == '-h':
         print ('test.py -i <gt> -o <gn>')
         sys.exit()
      elif opt in ("-i", "--ifile"):
         gt = arg
      elif opt in ("-o", "--ofile"):
         gn = arg
   print ('ground truth file is "', gt)
   print ('Output file is "', gn)
   mse_average(gt, gn)

if __name__ == "__main__":
   main(sys.argv[1:])