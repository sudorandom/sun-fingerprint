#!/usr/bin/env bash

set -ex

python3 generate-spectrum-image.py

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
	output/sun-spectrum-visible-fade-displate.jpg

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
	output/sun-spectrum-fade-displate.jpg

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
	output/sun-spectrum-fade-annotated-displate.jpg
