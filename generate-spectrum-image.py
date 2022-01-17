import csv
from PIL import Image, ImageDraw, ImageFont

ROW_WIDTH = 800
ROW_HEIGHT = 50

def main():
	colors = list(get_spectrum_colors())
	row_count = int(len(colors) / ROW_WIDTH)
	img = Image.new('RGB', (ROW_WIDTH, row_count*ROW_HEIGHT), color='black')
	draw = ImageDraw.Draw(img, 'RGBA')

	for i, color in enumerate(reversed(colors)):
		row_num = int(i / ROW_WIDTH)
		x_offset = i % ROW_WIDTH
		y_offset = row_num * ROW_HEIGHT
		draw.line((x_offset, y_offset, x_offset, y_offset+ROW_HEIGHT-2), fill=color)

	img.save("output.png", quality=100, subsampling=0)

	fnt = ImageFont.truetype("Roboto-Medium.ttf", 36)
	fnt_bold = ImageFont.truetype("Roboto-Bold.ttf", 40)
	draw.multiline_text((10, 10), "The Sun's Fingerprint", font=fnt_bold, fill=(255, 255, 255))
	draw.multiline_text((10, 100),
		"This is the spectrum of electromagnetic radiation\n"
		"that our star, the sun, outputs. The gaps that\n"
		"you see below are 'absorption lines'. Certain\n"
		"elements absorb different parts of the spectrum.\n"
		"This is one way that we know what the sun\n"
		"is made of.",
		font=fnt, fill=(255, 255, 255))

	draw.multiline_text((10, 500),
		"Here is infra-red. Humans eyes can't detect\n"
		"this frequency but the sun still emits in this\n"
		"frequency.", font=fnt, fill=(255, 255, 255))

	draw.multiline_text((10, 800), "Visible light starts here.", font=fnt, fill=(255, 255, 255))

	draw.multiline_text((10, 1800),
		"Here is ultra-violet. We don't see this either.\n"
		, font=fnt, fill=(255, 255, 255))

	draw.multiline_text((10, 2600),
		"It falls off pretty quickly. We aren't even close\n"
		"to X-Rays or Gamma waves. Only extremely\n"
		"powerful cosmic events produce emissions\n"
		"at these wavelengths."
		, font=fnt, fill=(255, 255, 255))

	img.save("output-annotated.png", quality=100, subsampling=0)


def get_spectrum_colors():
	# Sourced from https://www.nrel.gov/grid/solar-resource/spectra.html
	with open("AllMODEtr.txt") as f:
		read_tsv = list(csv.reader(f, delimiter="\t"))
		# (CM-1)
		# nm
		# MCebKur MChKur
		# MNewKur
		# MthKur
		# MoldKur
		# MODWherli_WMO
		rows = read_tsv[1:]
		c2 = [float(row[2]) for row in rows]
		top = max(c2)

		for i, row in enumerate(rows):
			val = float(row[2])
			a = int((val/top)*255)
			r, g, b = wav2RGB(float(row[1]))
			if r == g == b == 0:
				r = g = b = 255

			yield (r, g, b, a)


# https://codingmess.blogspot.com/2009/05/conversion-of-wavelength-in-nanometers.html
def wav2RGB(wavelength):
    w = int(wavelength)

    # colour
    if w >= 380 and w < 440:
        R = -(w - 440.) / (440. - 350.)
        G = 0.0
        B = 1.0
    elif w >= 440 and w < 490:
        R = 0.0
        G = (w - 440.) / (490. - 440.)
        B = 1.0
    elif w >= 490 and w < 510:
        R = 0.0
        G = 1.0
        B = -(w - 510.) / (510. - 490.)
    elif w >= 510 and w < 580:
        R = (w - 510.) / (580. - 510.)
        G = 1.0
        B = 0.0
    elif w >= 580 and w < 645:
        R = 1.0
        G = -(w - 645.) / (645. - 580.)
        B = 0.0
    elif w >= 645 and w <= 780:
        R = 1.0
        G = 0.0
        B = 0.0
    else:
        R = 0.0
        G = 0.0
        B = 0.0

    # intensity correction
    if w >= 380 and w < 420:
        SSS = 0.3 + 0.7*(w - 350) / (420 - 350)
    elif w >= 420 and w <= 700:
        SSS = 1.0
    elif w > 700 and w <= 780:
        SSS = 0.3 + 0.7*(780 - w) / (780 - 700)
    else:
        SSS = 0.0
    SSS *= 255

    return (int(SSS*R), int(SSS*G), int(SSS*B))


if __name__ == '__main__':
	main()
