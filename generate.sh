#!/usr/bin/env bash

set -ex

python3 generate-spectrum-image.py

# displate JPGs
convert output/sun-spectrum-visible-fade.png \
	-verbose -strip -auto-orient \
	-colorspace sRGB \
	-density 300 \
	-units pixelsperinch \
	-background black \
	-gravity center \
	-resize 4000x5600 \
	-extent 4000x5600 \
	-quality 100 \
	-brightness-contrast 20x20 \
	output/displate_sun-spectrum-visible-fade.jpg

convert output/sun-spectrum-fade.png \
	-verbose -strip -auto-orient \
	-colorspace sRGB \
	-density 300 \
	-units pixelsperinch \
	-background black \
	-gravity center \
	-resize 4000x5600 \
	-extent 4000x5600 \
	-quality 100 \
	-brightness-contrast 20x20 \
	output/displate_sun-spectrum-fade.jpg

convert output/sun-spectrum-fade-annotated.png \
	-verbose -strip -auto-orient \
	-colorspace sRGB \
	-density 300 \
	-units pixelsperinch \
	-background black \
	-gravity center \
	-resize 4000x5600 \
	-extent 4000x5600 \
	-quality 100 \
	-brightness-contrast 20x20 \
	output/displate_sun-spectrum-fade-annotated.jpg

# Instagram
convert output/sun-spectrum-visible-square.png \
	-verbose -strip -auto-orient \
	-colorspace sRGB \
	-density 300 \
	-units pixelsperinch \
	-background black \
	-gravity center \
	-resize 1080x1080\! \
	-extent 1080x1080\! \
	-quality 100 \
	-brightness-contrast 20x20 \
	output/instagram_sun-spectrum-visible-square.png

convert output/sun-spectrum-square.png \
	-verbose -strip -auto-orient \
	-colorspace sRGB \
	-density 300 \
	-units pixelsperinch \
	-background black \
	-gravity center \
	-resize 1080x1080\! \
	-extent 1080x1080\! \
	-quality 100 \
	-brightness-contrast 20x20 \
	output/instagram_sun-spectrum-square.png

convert output/sun-spectrum-square-annotated.png \
	-verbose -strip -auto-orient \
	-colorspace sRGB \
	-density 300 \
	-units pixelsperinch \
	-background black \
	-gravity center \
	-resize 1080x1080\! \
	-extent 1080x1080\! \
	-quality 100 \
	-brightness-contrast 20x20 \
	output/instagram_sun-spectrum-square-annotated.png
