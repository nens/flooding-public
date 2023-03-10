# -*- coding: utf-8 -*-
import logging
import os.path

from PIL import Image
from PIL import ImageFilter
from pkg_resources import resource_filename

from django.conf import settings

log = logging.getLogger('nens.symbol_manager')


class SymbolManager:
    def __init__(self, symbol_path):
        log.debug('Initializing SymbolManager')
        symbol_path = resource_filename(
            'flooding_visualization',
            'media/flooding_visualization/symbols')
        self.symbol_path = symbol_path
        self.generated_icon_path = os.path.join(
            settings.BUILDOUT_DIR, 'var', 'generated_icons')

        if not(os.path.exists(self.symbol_path)):
            log.critical('path %s does not exist' % self.symbol_path)
            raise Exception(
                'SymbolManager failed: path %s does not exist' %
                self.symbol_path)

    def get_symbol_transformed(self, filename_nopath, **kwargs):
        """Returns absolute filename of transformed symbol,

        if the transformed symbol does not yet exist, it is
        created. Transformation as follows:

        1) color, if given
        2) scale, if given
        3) rotate, if given
        4) shadow, if given

        input: filename_nopath is
        <symbol_path>\originals\<filename_nopath>

        kwargs:
        * size: (x, y)
        * color: (r, g, b) (alpha is unaltered)
        * rotate: in degrees, counterclockwise, around center
        * shadow_height: in pixels
        """
        log.debug('Entering get_symbol_transformed')

        SHADOW_FACTOR_Y = 1
        SHADOW_FACTOR_X = 0.5

        #get kwargs
        color = kwargs.get('color', (1.0, 1.0, 1.0, 1.0))
        fn_mask, = kwargs.get('mask', (filename_nopath,))
        sizex, sizey = kwargs.get('size', (0, 0))
        rotate, = kwargs.get('rotate', (0,))
        rotate %= 360
        shadow_height, = kwargs.get('shadow_height', (0,))
        force = kwargs.get('force', False)

        log.debug('color: %s' % str(color))
        log.debug('mask: %s' % fn_mask)
        log.debug('size: %dx%d' % (sizex, sizey))
        log.debug('rotate: %d' % (rotate))
        log.debug('shadow_height: %d' % (shadow_height))
        log.debug('force no cache: %s' % (force))

        filename_mask_abs = os.path.join(
            self.symbol_path, 'originals/', fn_mask)

        #result filename is :
        # <orig filename>_<mask>_<hex r><hex g>\
        # <hex b>_<sx>x<sy>_r<r>.<orig extension>
        fn_orig_base, fn_orig_extension = os.path.splitext(filename_nopath)
        result_filename_nopath = '%s_%s_%02x%02x%02x_%dx%d_r%03d_s%d%s' % (
            fn_orig_base, os.path.splitext(fn_mask)[0],
            min(255, color[0] * 256),
            min(255, color[1] * 256),
            min(255, color[2] * 256),
            sizex, sizey, rotate, shadow_height, fn_orig_extension)

        result_filename = os.path.join(
            self.generated_icon_path, result_filename_nopath)

        if os.path.isfile(result_filename) and force == False:
            log.debug('image already exists, returning filename')
        else:
            log.debug('generating image...')
            filename_orig_abs = os.path.join(
                self.symbol_path, 'originals/', filename_nopath)
            log.debug('orig filename: %s' % filename_orig_abs)
            if not(os.path.isfile(filename_orig_abs)):
                raise Exception('File not found (%s)' % filename_orig_abs)

            im = Image.open(filename_orig_abs)
            if im.mode != 'RGBA':
                im = im.convert('RGBA')

            #color
            im_mask = Image.open(filename_mask_abs)
            if im_mask.mode != 'RGBA':
                im_mask = im_mask.convert('RGBA')

            pix = im.load()  # create objects where you can read and
                             # write pixel values
            pix_mask = im_mask.load()
            for x in range(im.size[0]):
                for y in range(im.size[1]):
                    mask = pix_mask[x, y][3]
                    r, g, b, a = pix[x, y]
                    r = int(color[0] * r * mask / 256) + r * (255 - mask) / 256
                    g = int(color[1] * g * mask / 256) + g * (255 - mask) / 256
                    b = int(color[2] * b * mask / 256) + b * (255 - mask) / 256
                    pix[x, y] = (r, g, b, a)

            if sizex > 0 and sizey > 0:
                if sizex != im.size[0] or sizey != im.size[1]:
                    im = im.resize((sizex, sizey), Image.ANTIALIAS)

            #expand=True werkt niet goed: wordt niet meer deels doorzichtig
            if rotate > 0:
                im = im.rotate(rotate, Image.BICUBIC)

            #drop shadow
            #see also: http://en.wikipedia.org/wiki/Alpha_compositing, A over B
            if shadow_height > 0:
                im_shadow = Image.new('RGBA', im.size)
                im_shadow.paste((192, 192, 192, 255),
                                (int(shadow_height * SHADOW_FACTOR_X),
                                 int(shadow_height * SHADOW_FACTOR_Y)),
                                im)
                #now blur the im_shadow a little bit
                im_shadow = im_shadow.filter(ImageFilter.BLUR)

                #im_shadow.paste(im, (0,0))
                #paste original image on top, using the alpha channel
                pix = im.load()
                pix_shadow = im_shadow.load()
                log.debug('shadow x: %d' % im_shadow.size[0])
                for x in range(im_shadow.size[0]):
                    for y in range(im_shadow.size[1]):
                        r, g, b, a = pix_shadow[x, y]
                        r2, g2, b2, a2 = pix[x, y]
                        r_res = r2 * a2 / 256 + r * a * (255 - a2) / 256 / 256
                        g_res = g2 * a2 / 256 + g * a * (255 - a2) / 256 / 256
                        b_res = b2 * a2 / 256 + b * a * (255 - a2) / 256 / 256
                        a_res = a2 + (255 - a2) * a / 256
                        pix_shadow[x, y] = (r_res, g_res, b_res, a_res)

                im = im_shadow

            if os.path.isfile(result_filename):
                log.debug('deleting existing result file')
                os.remove(result_filename)

            log.debug('saving image (%s)' % result_filename)
            im.save(result_filename)

        return result_filename


def set_console_logger():
    #set log level to debug
    log.setLevel(logging.DEBUG)

    #create a console handler for logger
    h = logging.StreamHandler()
    h.setLevel(logging.DEBUG)
    formatter = logging.Formatter("%(levelname)s - %(message)s")
    h.setFormatter(formatter)
    logging.getLogger('').addHandler(h)


if __name__ == '__main__':
    # Basically just a test
    SYMBOLS_DIR = (
        '/media/drv0/repo/Products/LizardWeb/Trunk/System/resources/symbols')

    #set console logging
    set_console_logger()

    #start testing
    log.info('Testing SymbolManager...')
    sm = SymbolManager(SYMBOLS_DIR)
    sm.get_symbol_transformed('plus.png',
                              force=True,
                              mask='plus.png',
                              color=(0, 1, 0.5),
                              size=(16, 16),
                              rotate=0,
                              shadow_height=0,
                              )

    mask_list = ['plus_64.png', 'plus_64_mask.png']
    color_list = [(0, 0, 0), (1, 1, 1), (1, 0, 0), (0, 1, 1), (0.5, 1, 0.5)]
    size_list = [(16, 16), (32, 32)]
    rotate_list = [0, 30, 45, 180]
    shadow_height_list = [0, 2]

    for mask in mask_list:
        for color in color_list:
            for size in size_list:
                for rotate in rotate_list:
                    for shadow_height in shadow_height_list:
                        sm.get_symbol_transformed('plus_64.png',
                                                  force=True,
                                                  mask=mask,
                                                  color=color,
                                                  size=size,
                                                  rotate=rotate,
                                                  shadow_height=shadow_height,
                                                  )
