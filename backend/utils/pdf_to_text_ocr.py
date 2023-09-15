from PIL import Image, ImageSequence
import pytesseract

# Load the TIFF file
tiff_file_path = "backend/data/LOC.tiff"

# Open the TIFF file
tiff_file = Image.open(tiff_file_path)

# Initialize an empty string to collect the texts
text = ""

# If the TIFF file has multiple frames (pages), loop through each frame
for frame in ImageSequence.Iterator(tiff_file):
    # Convert the current frame to text and append it to the text string
    text += pytesseract.image_to_string(frame)

# Save the text to a file
with open("backend/data/output.txt", "w") as f:
    f.write(text)
