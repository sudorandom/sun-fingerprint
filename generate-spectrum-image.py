import csv
import cairo
import itertools
import numpy as np
from operator import itemgetter
from PIL import ImageColor
import random

ROW_WIDTH = 1000
ROW_HEIGHT = 50

WAVELENGTH_RANGES = [
    {'key': 'uv', 'start': 0, 'end': 400, 'label': 'UV', 'background-color': '#FF00FF'},
    {'key': 'visible', 'start': 400, 'end': 770, 'label': 'Visible Light', 'background-color': '#E0FBFC'},
    {'key': 'ir', 'start': 770, 'end': 1000, 'label': 'IR', 'background-color': '#FF3399'},
    {'key': 'radio_waves', 'start': 1000, 'end': 100000, 'label': 'Radio Waves', 'background-color': '#E5E5FF'},
]

KEY_ITEMGETTER = itemgetter('key')


def main():
    rows = list(get_spectrum_data_aggregated(nm_step=4, min_nm=0, max_nm=3000))
    print("Aggregated rows for full spectrum image", len(rows))
    write_image('output/sun-spectrum', rows, include_annotations=False)
    write_fade_image('output/sun-spectrum-fade', rows, include_annotations=False)
    write_fade_image('output/sun-spectrum-fade-annotated', rows, include_annotations=True)

    visible_rows = list(get_spectrum_data_aggregated(nm_step=5, min_nm=380, max_nm=700))
    print("Aggregated rows for visible spectrum image", len(visible_rows))
    write_image('output/sun-spectrum-visible', visible_rows, include_annotations=False)
    write_fade_image('output/sun-spectrum-visible-fade', visible_rows, include_annotations=False)


def write_fade_image(filename, rows, include_annotations=False):
    height = len(rows)
    width = int((1/1.4)*height)
    print("dimensions:", width, height)

    annotations = []
    if include_annotations:
        annotations = list(calculate_annotations(rows))

    with cairo.SVGSurface(filename+'.svg', width, height) as surface:
        ctx = cairo.Context(surface)
        ctx.save()
        ctx.set_source_rgba(0, 0, 0, 1)
        ctx.paint()
        ctx.restore()
        ctx.stroke()
        for i, row in enumerate(rows):
            x_offset = 0
            y_offset = i

            ctx.set_source_rgba(row['r']/255.0, row['g']/255.0, row['b']/255.0, row['a']/255.0)
            # ctx.rectangle(x_offset, y_offset, width, 1)
            # ctx.fill()
            ctx.set_line_width(1)
            ctx.move_to(x_offset, y_offset)
            ctx.line_to(x_offset+width, y_offset)
            ctx.stroke()

        for annotation in annotations:
            r, g, b = hex_to_rgb(annotation['background-color'])
            ctx.set_source_rgba(r/255, g/255, b/255, 0.5)
            ctx.rectangle(width*0.8+100, annotation['start_index'], width*0.18, annotation['end_index']-annotation['start_index'])
            ctx.fill()

            r, g, b = hex_to_rgb(annotation.get('text-color', '#FFFFFF'))
            ctx.set_source_rgba(r/255, g/255, b/255, 1)
            ctx.set_font_size(256)
            ctx.select_font_face("Courier", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
            text_x_offset = width*0.8+200
            text_y_offset = annotation['start_index']+400
            ctx.move_to(text_x_offset, text_y_offset)
            ctx.show_text(annotation['label'])
            text_extents = ctx.text_extents(annotation['label'])
            ctx.move_to(text_x_offset, text_y_offset+(text_extents.height*2))
            ctx.set_font_size(192)
            ctx.select_font_face("Courier", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
            ctx.show_text(f"{format_nm(annotation['start'])}-{format_nm(annotation['end'])}")


        surface.write_to_png(filename+'.png')


def hex_to_rgb(hex_color):
    return ImageColor.getcolor(hex_color, "RGB")


def calculate_annotations(rows):
    if len(rows) == 0:
        return []

    current_ranges = set()
    range_beginnings = []
    range_endings = []
    for i, row in enumerate(rows):
        new_current_ranges = set()
        for r in WAVELENGTH_RANGES:
            frozen_r = frozenset(r.items())
            if row['nm'] > r['start'] and row['nm'] < r['end']:
                new_current_ranges.add(frozen_r)
                if frozen_r not in current_ranges:
                    range_beginnings.append({'start_index': i} | r)

        for r in current_ranges - new_current_ranges:
            range_endings.append({'end_index': i} | dict(r))

        current_ranges = new_current_ranges

    for r in current_ranges:
        range_endings.append({'end_index': i} | dict(r))

    for b, e in zip(
        sorted(range_beginnings, key=KEY_ITEMGETTER),
        sorted(range_endings, key=KEY_ITEMGETTER)):
        yield {**b, **e}


def write_image(filename, rows, include_annotations=False):
    row_count = int(len(rows) / ROW_WIDTH) + 1
    width = min(len(rows), ROW_WIDTH)

    with cairo.SVGSurface(filename+'.svg', width, row_count*ROW_HEIGHT) as surface:
        ctx = cairo.Context(surface)
        ctx.save()
        ctx.set_source_rgba(0, 0, 0, 1)
        ctx.paint()
        ctx.restore()
        ctx.stroke()
        for i, row in enumerate(reversed(rows)):
            row_num = int(i / width)
            x_offset = i % width
            y_offset = row_num * ROW_HEIGHT

            ctx.set_source_rgba(row['r']/255, row['g']/255, row['b']/255, row['a']/255)
            ctx.move_to(x_offset, y_offset)
            ctx.line_to(x_offset, y_offset+ROW_HEIGHT-2)
            ctx.stroke()

        surface.write_to_png(filename+'.png')


def get_spectrum_data_aggregated(min_nm=None, max_nm=None, nm_step=20):
    all_rows = list(get_spectrum_data(min_nm=min_nm, max_nm=max_nm))
    m = {}
    lowest = float('inf')
    highest = float('-inf')
    round_nm_factor = 100/nm_step
    round_nm = lambda nm: int(nm*round_nm_factor)
    for nm, rows in itertools.groupby(all_rows, lambda row: round_nm(row['nm'])*round_nm_factor):
        rows = list(rows)
        nm_rounded = round_nm(rows[0]['nm'])
        highest = max(nm_rounded, highest)
        lowest = min(nm_rounded, lowest)
        m[nm_rounded] = {
          'nm': nm_rounded/round_nm_factor,
           'r': rows[0]['r'],
           'g': rows[0]['g'],
           'b': rows[0]['b'],
           'a': int(sum(row['a'] for row in rows)/len(rows)),
         }

    for nm in range(lowest, highest, nm_step):
        row = m.get(nm, {
            'nm': nm/round_nm_factor,
            'r': 0,
            'g': 0,
            'b': 0,
            'a': 0,
        })
        yield row


def get_spectrum_data(min_nm=None, max_nm=None):
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
        c2 = np.array([float(row[2]) for row in rows if should_include_entry(float(row[1]), min_nm, max_nm)])
        bottom = np.percentile(c2, 10)
        # bottom = np.min(c2)
        # top = np.max(c2)
        top = np.percentile(c2, 70)

        print(f"requested range: {min_nm}nm - {max_nm}nm")
        print(f"intensity range: {np.min(c2)} - {np.max(c2)}")
        print(f"brightness range: {bottom} - {top}")

        for i, row in enumerate(rows):
            val = float(row[2])
            a = int(val/bottom/top*255)
            nm = float(row[1])
            r, g, b = wav2RGB(nm)

            if not should_include_entry(nm, min_nm, max_nm):
                continue

            if r == g == b == 0:
                r = g = b = 255

            yield {'nm': nm, 'r': r, 'g': g, 'b': b, 'a': a}


def should_include_entry(nm, min_nm, max_nm):
    if min_nm is not None and nm < min_nm:
        return False
    if max_nm is not None and nm > max_nm:
        return False
    return True


# https://codingmess.blogspot.com/2009/05/conversion-of-wavelength-in-nanometers.html
def wav2RGB(wavelength):
    w = int(wavelength)

    # colour
    if w < 400:
        R = 1.0
        G = -(w - 400.) / (400. - 200.)
        B = 1.0
    elif w >= 400 and w < 440:
        R = -(w - 440.) / (440. - 400.)
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
    elif w > 780 and w <= 1000:
        R = 1.0
        G = 0.2
        B = 0.6
    elif w > 1000:
        R = 0.9
        G = 0.9
        B = 1.0
    else:
        R = 0.0
        G = 0.0
        B = 0.0

    # intensity correction
    # if w >= 380 and w < 420:
    #     SSS = 0.3 + 0.7*(w - 350) / (420 - 350)
    # elif w >= 420 and w <= 700:
    #     SSS = 1.0
    # elif w > 700 and w <= 780:
    #     SSS = 0.3 + 0.7*(780 - w) / (780 - 700)
    # else:
    #     SSS = 0.0
    SSS = 1
    SSS *= 255

    return (int(SSS*R), int(SSS*G), int(SSS*B))


def format_nm(nm):
    if nm >= 1000:
        return f"{int(nm/1000)}µm"
    else:
        return f"{nm}nm"


if __name__ == '__main__':
    main()
