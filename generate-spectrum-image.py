import csv
import cairo
import itertools

ROW_WIDTH = 1000
ROW_HEIGHT = 50

def main():
    rows = list(get_spectrum_data_aggregated())
    write_image('output/sun-spectrum', rows, include_text=False)
    write_image('output/sun-spectrum-annotated', rows, include_text=True)

    visible_rows = list(get_spectrum_data_aggregated(only_visible=True))
    write_image('output/sun-spectrum-visible', visible_rows, include_text=False)


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

        if include_text:
            ctx.set_source_rgba(1, 1, 1, 1)
            ctx.select_font_face("Roboto", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
            ctx.set_font_size(68)
            ctx.move_to(120, 65)
            ctx.show_text("The Sun's Fingerprint")

            fs = 36
            ctx.set_font_size(fs)
            ctx.move_to(10, 120)
            ctx.show_text("This is the spectrum of electromagnetic radiation that our")
            ctx.move_to(10, 120+fs)
            ctx.show_text("star, the sun, outputs. The gaps that you see below are")
            ctx.move_to(10, 120+fs*2)
            ctx.show_text("'absorption lines'.")

            ctx.move_to(10, 430)
            ctx.show_text("Here is infra-red. Humans eyes can't detect this frequency")
            ctx.move_to(10, 430+fs)
            ctx.show_text("but the sun still emits in this frequency.")

            ctx.move_to(10, 686)
            ctx.show_text("Visible light starts here.")

            ctx.move_to(10, 1385)
            ctx.show_text("Here is ultra-violet. We can't see this either.")

        surface.write_to_png(filename+'.png')


def get_spectrum_data_aggregated(only_visible=False):
    rows = get_spectrum_data(only_visible=only_visible)
    for nm, rows in itertools.groupby(rows, lambda row: int(row['nm']*40)):
        rows = list(rows)
        yield {
          'nm': rows[0]['nm'],
          'r': rows[0]['r'],
          'g': rows[0]['g'],
          'b': rows[0]['b'],
          'a': int(sum(row['a'] for row in rows)/len(rows)),
        }


def get_spectrum_data(only_visible=False):
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
            nm = float(row[1])
            r, g, b = wav2RGB(nm)
            if only_visible and (r == g == b == 0):
                continue

            if r == g == b == 0:
                r = g = b = 255

            yield {'nm': nm, 'r': r, 'g': g, 'b': b, 'a': a}


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
