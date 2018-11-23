#!/usr/bin/env python3

import xml.etree.ElementTree as ET
from PIL import Image
import os

VARIABILITY_DICT = {
    'blur': {
        '0': 'clear',
        '1': 'normal_blur',
        '2': 'heavy blur',
    },
    'expression': {
        '0': 'typical expression',
        '1': 'exaggerate expression',
    },
    'illumination': {
        '0': 'normal illumination',
        '1': 'extreme illumination',
    },
    'occlusion': {
        '0': 'no occlusion',
        '1': 'partial occlusion',
        '2': 'heavy occlusion',
    },
    'pose': {
        '0': 'typical pose',
        '1': 'atypical pose',
    },
    'invalid': {
        '0': 'valid image',
        '1': 'invalid image',
    }

}

def createAnnotationPascalVocTree(folder, basename, path, width, height):
    annotation = ET.Element('annotation')
    ET.SubElement(annotation, 'folder').text = folder
    ET.SubElement(annotation, 'filename').text = basename
    ET.SubElement(annotation, 'path').text = path

    source = ET.SubElement(annotation, 'source')
    ET.SubElement(source, 'database').text = 'Unknown'

    size = ET.SubElement(annotation, 'size')
    ET.SubElement(size, 'width').text = width
    ET.SubElement(size, 'height').text = height
    ET.SubElement(size, 'depth').text = '3'

    ET.SubElement(annotation, 'segmented').text = '0'

    return ET.ElementTree(annotation)


def createObjectPascalVocTree(xmin, ymin, xmax, ymax, blur,
                              expr, illum, invalid, occl, pose):

    obj = ET.Element('object')
    ET.SubElement(obj, 'name').text = 'face'
    ET.SubElement(obj, 'pose').text = 'Unspecified'
    ET.SubElement(obj, 'truncated').text = '0'

    bndbox = ET.SubElement(obj, 'bndbox')
    ET.SubElement(bndbox, 'xmin').text = xmin
    ET.SubElement(bndbox, 'ymin').text = ymin
    ET.SubElement(bndbox, 'xmax').text = xmax
    ET.SubElement(bndbox, 'ymax').text = ymax

    ET.SubElement(obj, 'blur').text = blur
    ET.SubElement(obj, 'expression').text = expr
    ET.SubElement(obj, 'illumination').text = illum
    ET.SubElement(obj, 'invalid').text = invalid
    ET.SubElement(obj, 'occlusion').text = occl
    ET.SubElement(obj, 'pose').text = pose


    return ET.ElementTree(obj)


def parseImFilename(imFilename, imPath):
    im = Image.open(os.path.join(imPath, imFilename))
            
    folder, basename = imFilename.split('/')
    width, height = im.size

    return folder, basename, imFilename, str(width), str(height)

def convert_variability_to_string(blur, expr, illum, invalid, occl, pose):
    blur = VARIABILITY_DICT['blur'][blur]
    expr = VARIABILITY_DICT['expression'][expr]
    illum = VARIABILITY_DICT['illumination'][illum]
    invalid = VARIABILITY_DICT['invalid'][invalid]
    occl = VARIABILITY_DICT['occlusion'][occl]
    pose = VARIABILITY_DICT['pose'][pose]

    return blur, expr, illum, invalid, occl, pose

def convertWFAnnotations(annotationsPath, targetPath, imPath):
    ann = None
    basename = ''
    with open(annotationsPath) as f:
        while True:
            imFilename = f.readline().strip()
            if imFilename:
                folder, basename, path, width, height = parseImFilename(imFilename, imPath)
                ann = createAnnotationPascalVocTree(folder, basename, os.path.join(imPath, path), width, height)
                nbBndboxes = f.readline()
                i = 0
                while i < int(nbBndboxes):
                    i = i + 1
                    x1, y1, w, h, blur, expr, illum, invalid, occl, pose = [int(j) for j in f.readline().split()]
                    blur, expr, illum, invalid, occl, pose = convert_variability_to_string(str(blur),
                                                                                           str(expr),
                                                                                           str(illum),
                                                                                           str(invalid),
                                                                                           str(occl),
                                                                                           str(pose))
                    ann.getroot().append(createObjectPascalVocTree(str(x1),
                                                                   str(y1),
                                                                   str(x1 + w),
                                                                   str(y1 + h),
                                                                   blur,
                                                                   expr,
                                                                   illum,
                                                                   invalid,
                                                                   occl,
                                                                   pose).getroot())

                if not os.path.exists(targetPath):
                     os.makedirs(targetPath)
                annFilename = os.path.join(targetPath, basename.replace('.jpg', '.xml'))
                ann.write(annFilename)
                print('{} => {}'.format(basename, annFilename), flush=True)
            else:
                break 
    f.close()


if __name__ == '__main__':
    import argparse

    PARSER = argparse.ArgumentParser()
    PARSER.add_argument('-ap', '--annotations-path', help='the annotations file path. ie:"./wider_face_split/wider_face_train_bbx_gt.txt".')
    PARSER.add_argument('-tp', '--target-path', help='the target directory path where XML files will be copied.')
    PARSER.add_argument('-ip', '--images-path', help='the images directory path. ie:"./WIDER_train/images"')

    ARGS = vars(PARSER.parse_args())
    
    convertWFAnnotations(ARGS['annotations_path'], ARGS['target_path'], ARGS['images_path'])

