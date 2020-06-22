import numpy as np
import matplotlib.pyplot as plt
import matplotlib.image as mpimg

import argparse, re, json

TEMPLATE_PATH = './template.lua'
DEFAULT_EXPORT_PATH = './ship.lua'
FLOAT_RE = r"(?:[-+]?\d*\.\d+|\d+)"
COLOR_LIST = [830, 801, 826] # type of blocks used as pixel
GRAY_SCALE = [0, 0.82, 0.83]

def pprint(json_thing, sort=True, indents=4):
    if type(json_thing) is str:
        print(json.dumps(json.loads(json_thing), sort_keys=sort, indent=indents))
    else:
        print(json.dumps(json_thing, sort_keys=sort, indent=indents))
    return None

def rgb2gray(rgb):
    return np.dot(rgb[...,:3], [0.2989, 0.5870, 0.1140])

def process(blocks, imagePath):
    img = mpimg.imread(imagePath)     
    gray = rgb2gray(img)
    IMAGE_SIZE_Y, IMAGE_SIZE_X = gray.shape

    blocks = [b for b in blocks if b['data'][0] in COLOR_LIST]
    sorted(blocks, key=lambda d:d['data'][1])

    xs = [b['data'][1] for b in blocks]
    origin = [min(x[0] for x in xs), min(x[1] for x in xs)]
    width = max(x[0] for x in xs)-min(x[0] for x in xs) 
    hight = max(x[1] for x in xs)-min(x[1] for x in xs)
    step_j = width/(IMAGE_SIZE_Y-1)
    step_i = hight/(IMAGE_SIZE_X-1)

    for block_i in range(len(blocks)):
        block = blocks[block_i]
        x, y = block['data'][1]
        j = int((x-origin[0])/step_j)
        i = IMAGE_SIZE_Y-1-int((y-origin[1])/step_i)
        old_color = block['data'][0]

        for level in range(len(GRAY_SCALE)):
            if gray[i, j] >= GRAY_SCALE[level]:
                block['data'][0] = COLOR_LIST[level]

        if block['data'][0] != old_color:
            block['changed'] = True
            if len(block['data'])>2:
                block['data'] = block['data'][:2]
    return blocks

def parseBlocks(rawdata):
    pattern = re.compile("\{\d+, \{%s, %s\}(?:, %s)?\}" % (FLOAT_RE, FLOAT_RE, FLOAT_RE))
    matches = re.findall(pattern, rawdata)
    blocks = [
        {
            'changed': False,
            'data': json.loads(match.replace('{', '[').replace('}', ']')),
            'old': match
        } for match in matches
    ]
    return blocks

def loadTemplate(path=TEMPLATE_PATH):
    with open(path, 'r')as f:
        rawdata = f.read()
    return rawdata

def saveShip(template, blocks, path=DEFAULT_EXPORT_PATH):
    for block in blocks:
        if block['changed']:
            # print('changed: %s' % (block))
            new = json.dumps(block['data']).replace('[', '{').replace(']', '}')
            # print(block['old'], new)
            template = template.replace(block['old'], new)
    with open(path, 'w') as f:
        f.write(template)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("imagePath", help="input image path",
                type=str)
    args = parser.parse_args()
    template = loadTemplate(TEMPLATE_PATH)
    blocks = parseBlocks(template)
    process(blocks, imagePath=args.imagePath)
    saveShip(template, blocks)