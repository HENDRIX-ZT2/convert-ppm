import argparse
import logging
import os
import numpy as np
from struct import pack, unpack

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)


def ensure_ext(filepath, ext):
	return f"{os.path.splitext(filepath)[0]}{ext}"


def read_image(height, stream, width):
	data = np.empty((height, width, 4), dtype=np.uint8)
	stream.readinto(data)
	return data


def read_tga(filepath):
	logging.info(f"Reading {os.path.basename(filepath)}")
	with open(filepath, 'rb') as stream:
		a, b, c, d, e, x_ori, y_ori, width, height, f, g = unpack("3B H B 4H 2B", stream.read(18))
		data = read_image(height, stream, width)
	return data[::-1, :, (2, 1, 0, 3)]


def write_tga(filepath, data):
	filepath = ensure_ext(filepath, ".tga")
	logging.info(f"Writing {os.path.basename(filepath)}")
	HEIGHT, WIDTH, col_i = data.shape
	x_ori = 0
	y_ori = HEIGHT
	header = pack("3B H B 4H 2B", 0, 0, 2, 0, 0, x_ori, y_ori, WIDTH, HEIGHT, 32, 8)
	with open(filepath, 'wb') as f:
		f.write(header)
		f.write(data[::-1, :, (2, 1, 0, 3)].tobytes())


def read_ppm(filepath):
	logging.info(f"Reading {os.path.basename(filepath)}")
	with open(filepath, 'rb') as stream:
		magic, comment, dim, nc, rest = stream.read(100).split(b"\n")
		x, y = dim.split(b" ")
		width = int(x)
		height = int(y)
		maxval = int(nc)
		header = b"\n".join( (magic, comment, dim, nc ) )
		stream.seek(len(header)+1)
		return read_image(height, stream, width)


def write_ppm(filepath, data):
	filepath = ensure_ext(filepath, ".ppm")
	logging.info(f"Writing {os.path.basename(filepath)}")
	height, width, col_i = data.shape
	with open(filepath, 'wb') as f:
		f.write( b"\n".join( (b"P7", b"# File created by Blue Tongue Software's PPM Photoshop format plugin.", f"{width} {height}".encode(), b"255", data.tobytes()) ) )


def resize(folder, output=".ppm"):
	for name in os.listdir(folder):
		filepath = os.path.join(folder, name)
		if "ppm" in output.lower():
			if name.lower().endswith(".tga"):
				write_ppm(filepath, read_tga(filepath))
		else:
			if name.lower().endswith(".ppm"):
				write_tga(filepath, read_ppm(filepath))


if __name__ == '__main__':
	parser = argparse.ArgumentParser(prog='convert-ppm')
	parser.add_argument('dir', nargs='?', help='Folder containing all .ppm or .tga files')
	parser.add_argument('output', nargs='?', help='Output format - .ppm or .tga')
	args = parser.parse_args()
	resize(args.dir, args.output)