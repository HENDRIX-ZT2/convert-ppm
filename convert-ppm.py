import os
import numpy as np
from struct import pack, unpack

def read_tga(name):
	tga_name = name[:-4]+".tga"
	print("\nReading",os.path.basename(tga_name))
	with open(tga_name, 'rb') as f:
		datastream = f.read()
	a, b, c, d, e, x_ori, y_ori, WIDTH, HEIGHT, f, g = unpack("3B H B 4H 2B", datastream[0:18])
	data = np.frombuffer(datastream[18:], dtype=np.uint8)
	data = np.reshape(data, (HEIGHT, WIDTH, 4))
	out = np.zeros((HEIGHT, WIDTH, 4), dtype=np.uint8)
	for x in range(0, HEIGHT):
		for y in range(0, WIDTH):
			r, g, b, a = data[x,y]
			out[x,y] = [b, g, r, a]
	return np.flipud(out)
	
def write_tga(name, data):
	tga_name = name[:-4]+".tga"
	print("\nWriting",os.path.basename(tga_name))
	HEIGHT,WIDTH, col_i = data.shape
	x_ori = 0
	y_ori = HEIGHT
	header = pack("3B H B 4H 2B", 0, 0, 2, 0, 0, x_ori, y_ori, WIDTH, HEIGHT, 32, 8)
	out = np.zeros((HEIGHT, WIDTH, 4), dtype=np.uint8)
	for x in range(0, HEIGHT):
		for y in range(0, WIDTH):
			r, g, b, a = data[x,y]
			out[x,y] = [b, g, r, a]
	bbytes = np.flipud(out).tobytes()
	with open(tga_name, 'wb') as f:
		f.write(b"".join( (header, bbytes)) )
	print(x,y,col_i)
	
def read_ppm(name):
	print("\nReading",os.path.basename(name))
	with open(name, 'rb') as f:
		datastream = f.read()
	magic, comment, dim, nc, rest = datastream[0:100].split(b"\n")
	x, y = dim.split(b" ")
	WIDTH = int(x)
	HEIGHT = int(y)
	MAXVAL = int(nc)
	header = b"\n".join( (magic, comment, dim, nc ) )
	start = len(header)+1
	data = np.frombuffer(datastream[start:start+(WIDTH*HEIGHT*4)], dtype=np.uint8)
	data = np.reshape(data, (HEIGHT, WIDTH, 4))
	return data
	
def write_ppm(name, data):
	ppm_name = name[:-4]+".ppm"
	print("\nWriting",os.path.basename(ppm_name))
	HEIGHT,WIDTH, col_i = data.shape
	with open(ppm_name, 'wb') as f:
		f.write( b"\n".join( (b"P7", b"# File created by Blue Tongue Software's PPM Photoshop format plugin.", (str(WIDTH)+" "+str(HEIGHT)).encode(), b"255", data.tobytes()) ) )

def ppm_2_tga(name):
	data = read_ppm(name)
	write_tga(name, data)
	
def tga_2_ppm(name):
	data = read_tga(name)
	write_ppm(name, data)

# def show_data(data):
	# from matplotlib import pyplot as plt
	# plt.imshow(data2, interpolation='nearest')
	# plt.show()

dir = "C:/Program Files (x86)/Universal Interactive/Blue Tongue Software/Jurassic Park Operation Genesis/JPOG/Data/Particle"

#convert PPM to TGA
for f in os.listdir(dir):
	if f.lower().endswith(".ppm"):
		filepath = os.path.join(dir, f)
		ppm_2_tga( filepath )
		
# #convert TGA to PPM
# for f in os.listdir(dir):
	# if f.lower().endswith(".tga"):
		# filepath = os.path.join(dir, f)
		# tga_2_ppm( filepath )