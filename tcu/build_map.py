import argparse
import shutil
import json
import os

from PIL import Image


def tileset_make(img, tile_path, tile_size=256, max_zoom=-1):
    # save full image, mainly for debugging
    os.makedirs(tile_path, exist_ok=True)
    img.save(os.path.join(tile_path, 'full.png'))

    # determine zoom levels
    sz = img.size
    max_width = max(*sz)
    zooms = 0
    w = tile_size
    while w <= max_width:
        zooms = zooms + 1
        w = w * 2

    # save tiles
    zimgs = [None] * zooms
    zimgs[-1] = img
    for z in range(zooms):
        zlevel = zooms - 1 - z
        zpath = tile_path + '/{}'.format(zlevel)
        print('Generate Zoom: {}'.format(zpath))

        # shrink image
        if zimgs[zlevel] is None:
            zimgs[zlevel] = zimgs[zlevel + 1].resize((sz[0] >> z, sz[1] >> z), Image.LANCZOS)

        if not os.path.isdir(zpath):
            for x in range(0, 2 ** zlevel):
                dpath = os.path.join(zpath, '{}'.format(x))
                os.makedirs(dpath, exist_ok=True)
                for y in range(0, 2 ** zlevel):
                    fpath = os.path.join(dpath, '{}.png'.format(y))
                    zimgs[zlevel].crop((x * tile_size, y * tile_size, (x + 1) * tile_size, (y + 1) * tile_size)).save(
                        fpath)

    for zlevel in range(zooms, max_zoom + 1):
        width = tile_size >> (zlevel - (zooms - 1))
        zpath = os.path.join(tile_path, '{}'.format(zlevel))
        print('Generate Zoom: {}'.format(zpath))
        if not os.path.isdir(zpath):
            for x in range(0, 2 ** zlevel):
                dpath = os.path.join(zpath, '{}'.format(x))
                os.makedirs(dpath, exist_ok=True)
                for y in range(0, 2 ** zlevel):
                    fpath = os.path.join(dpath, '{}.png'.format(y))
                    img = zimgs[(zooms - 1)]
                    img = img.crop((x * width, y * width, (x + 1) * width, (y + 1) * width))
                    img = img.resize((tile_size, tile_size), Image.NEAREST)
                    img.save(fpath)


def build_map(background, spheres):
    dpath = 'build'
    # process background
    org = Image.open(background)
    new_size = ((org.width + 256 - 1) // 256 * 256, (org.height + 256 - 1) // 256 * 256)
    new_size = max(*new_size)
    new_size = 8192
    new_size = (new_size, new_size)

    bck = Image.new('RGB', new_size, 0)

    h_offset = (bck.width - org.width) // 2
    v_offset = (bck.height - org.height) // 2

    bck.paste(org, (h_offset, v_offset))

    tileset_make(bck, os.path.join(dpath, 'bck'))

    # copy library files
    copy_support_files = True
    if copy_support_files:
        dst = os.path.join(dpath, 'index.html')
        if os.path.exists(dst):
            print('WARNING: {} already exists will not over-write'.format(dst))
        else:
            shutil.copyfile(os.path.join('tcu', 'static', 'index.html'), dst)

        dst = os.path.join(dpath, 'lib')
        if os.path.exists(dst):
            print('WARNING: {} already exists will not over-write'.format(dst))
        else:
            shutil.copytree(os.path.join('tcu', 'static', 'lib'), dst)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        'background', type=str, help='Background image')

    parser.add_argument(
        'spheres', type=str, default=None,
        help='Root directory of spheres')

    args = parser.parse_args()

    build_map(args.background, args.spheres)


if __name__ == "__main__":
    main()