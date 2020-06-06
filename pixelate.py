from PIL import Image

hw_ratios = {

}

# 1 set         55         5 x 11
# 2 set        110         10 x 11
# 3 set        165         11 x 15


# Open Paddington
img = Image.open("paddington.png")

# Resize smoothly down to 16x16 pixels
imgSmall = img.resize((16,16),resample=Image.BILINEAR)

# Scale back up using NEAREST to original size
result = imgSmall.resize(img.size,Image.NEAREST)

# Save
result.save('result.png')
