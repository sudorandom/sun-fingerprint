import csv
import cairo
import itertools
import numpy as np
import random

ROW_WIDTH = 1000
ROW_HEIGHT = 50

def main():
    rows = list(get_spectrum_data_aggregated(nm_step=4, min_nm=0, max_nm=3000))
    print("Aggregated rows for full spectrum image", len(rows))
    write_image('output/sun-spectrum', rows, include_text=False)
    write_fade_image('output/sun-spectrum-fade', rows, include_text=False)
    # write_image('output/sun-spectrum-annotated', rows, include_text=True)

    visible_rows = list(get_spectrum_data_aggregated(nm_step=5, min_nm=380, max_nm=700))
    print("Aggregated rows for visible spectrum image", len(visible_rows))
    # write_image('output/sun-spectrum-visible', visible_rows, include_text=False)
    write_fade_image('output/sun-spectrum-visible-fade', visible_rows, include_text=False)

def write_fade_image(filename, rows, include_text=False):
    height = len(rows)
    width = int((1/1.4)*height)
    print("dimensions:", width, height)

    with cairo.SVGSurface(filename+'.svg', width, height) as surface:
        ctx = cairo.Context(surface)
        ctx.save()
        ctx.set_source_rgba(0, 0, 0, 1)
        ctx.paint()
        ctx.restore()
        ctx.stroke()
        random.seed(10)
        # curve_height = random.randrange(-50, 50)
        # curve_width = random.randrange(width/10, width/2)
        for i, row in enumerate(reversed(rows)):
            # if i % 100:
            #     curve_height = random.randrange(-50, 50)
            #     curve_width = random.randrange(width/10, width/2)
            x_offset = 0
            y_offset = i

            ctx.set_source_rgba(row['r']/255.0, row['g']/255.0, row['b']/255.0, row['a']/255.0)
            # ctx.set_source_rgba(row['a']/255.0, row['a']/255.0, row['a']/255.0, row['a']/255.0)
            # ctx.curve_to(x_offset, y_offset, x_offset+curve_width, y_offset-curve_height, width, y_offset)
            ctx.rectangle(x_offset, y_offset, len(rows), 1)
            ctx.stroke()

        surface.write_to_png(filename+'.png')


def write_image(filename, rows, include_text=False):
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
          'nm': nm_rounded*round_nm_factor,
           'r': rows[0]['r'],
           'g': rows[0]['g'],
           'b': rows[0]['b'],
           'a': int(sum(row['a'] for row in rows)/len(rows)),
         }

    print(lowest, highest, nm_step)
    for nm in range(lowest, highest, nm_step):
        row = m.get(nm, {
            'nm': nm*round_nm_factor,
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
        bottom = np.percentile(c2, 30)
        # bottom = np.min(c2)
        top = np.max(c2)

        print(bottom, top)

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
