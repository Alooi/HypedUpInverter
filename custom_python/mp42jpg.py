from models.helpers import get_landmark
import cv2


def make_seq(path='../../../../ibex/scratch/nasseraa/Untitled.mp4'):
    vidcap = cv2.VideoCapture(path)
    success,image = vidcap.read()
    count = 0
    while success:
        cv2.imwrite("./data/RTT/frame%d.jpg" % count, image)     # save frame as JPEG file      
        success,image = vidcap.read()
        print('Read a new frame: ', success, 'frame #', count, end="\r")
        count += 1
    print("\nsuccessfully wrote", count, "frames")

def quick_decoder(image):
    pass # implement the quick decoder here

if __name__ == "__main__":
    make_seq()