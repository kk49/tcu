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


def build_map(background, spheres_path):
    dpath = 'build'
    map_size = 256.0
    universe_size = 1024.0
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

    # find spheres
    spheres = []
    for sd_rel in os.listdir(spheres_path):
        sd_abs = os.path.join(spheres_path, sd_rel)
        if os.path.isdir(sd_abs):
            config = os.path.join(sd_abs, 'sphere.json')
            if os.path.isfile(config):
                with open(config, 'r') as f:
                    sphere_config = json.load(f)
                spheres.append([sphere_config, sd_rel, sd_abs])
            else:
                print(f'WARNING: {sd_abs} missing sphere.json')

    # make spheres
    shutil.rmtree(os.path.join(dpath, 'data'), ignore_errors=True)
    os.makedirs(os.path.join(dpath, 'data'), exist_ok=True)
    with open(os.path.join(dpath, 'data', 'spheres.js'), 'w') as f:
        for sphere_config, sd_rel, sd_abs in spheres:
            # copy image
            has_image = False
            if 'image' in sphere_config:
                rel_img = sphere_config['image']
                src_img = os.path.abspath(os.path.join(sd_abs, rel_img))
                web_img = os.path.join('data', sd_rel, rel_img)
                dst_img = os.path.abspath(os.path.join(dpath, web_img))
                os.makedirs(os.path.split(dst_img)[0], exist_ok=True)
                shutil.copy(src_img, dst_img)
                img = Image.open(dst_img)
                x0, y0 = sphere_config['position']
                x = map_size / 2.0 + x0 / universe_size * map_size
                y = -map_size / 2.0 + y0 / universe_size * map_size

                szx = sphere_config['size']
                szy = szx * img.height / img.width
                image_bounds = [[y - szy, x - szx], [y + szy, x + szx]]

                f.write('let obj = L.imageOverlay("{}", {}, {{alt: "{}", interactive:true, className: "crisp-image"}});\n'.format(
                    web_img, image_bounds, sphere_config['name']
                ))

                f.write(
                    f'obj.bindPopup("" +\n'
                    f'  "<strong>Name:</strong> {sphere_config["name"]}<br>" +\n'
                    f'  "<strong>Author:</strong> {sphere_config["author"]}<br>" +\n'
                    f'  "<strong>Link:</strong> {sphere_config["link"]}<br>" +\n'
                    f'  "{sphere_config["description"]}<br>" +\n'
                    f'  "<small>{sphere_config["image_src"]}</small>");\n'
                    )

                f.write('obj.addTo(map);\n')

        '''
            imageUrl = 'data/earth/PIA21961.png';
        x = 128;
        y = -128;
        scale = 2;
        szx = scale;
        szy = scale * 938.0 / 1672.0;
        imageBounds = [[y-szy,x-szx], [y+szy,x+szx]];
        earth = L.imageOverlay(
            imageUrl,
            imageBounds,
            {alt: "Earth", interactive:true, className: 'crisp-image'}
        );
        earth.bindPopup("" +
            "<strong>Name:</strong> Earth<br>" +
            "<strong>Author:</strong> Wouldn't you like to know<br>" +
            "<strong>Link:</strong> <a href='https://en.wikipedia.org/wiki/Earth' target='_blank'>Wikipedia: Earth</a><br>" +
            "It's alright, I guess.<br>" +
            "<small><a href='https://photojournal.jpl.nasa.gov/catalog/PIA21961' target='_blank'>Image Source</a></small>");
        earth.addTo(map);
        map.openPopup(earth.getPopup().getContent(), [-128,128], {});
        '''
        pass

    # copy library files
    copy_support_files = True
    if copy_support_files:
        dst = os.path.join(dpath, 'index.html')
        if False and os.path.exists(dst):
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