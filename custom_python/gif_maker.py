import glob
from PIL import Image
def make_gif(frame_folder):
    frames = [Image.open(image) for image in glob.glob(f"{frame_folder}/*.jpg")]
    # reduce image quality
    for frame in frames:
        frame.save(frame.filename, optimize=True, quality=10)
    frames[0].save(
        f"./gifs/GT.gif",
        format="gif",
        optimize=True,
        append_images=frames[1:],
        save_all=True,
        duration=33,
        loop=0,
    )
    for frame in frames:
        frame.close()
    

# convert png to mp4

if __name__ == "__main__":
    make_gif("../../../../ibex/scratch/nasseraa/clip-long-test-100-aligned")
