import pathlib
import os
import tensorflow as tf
from PIL import Image
import numpy as np
import argparse
import sys
sys.path.append("modules/object_detect/models/research")
from modules.object_detect.models.research import object_detection
from modules.object_detect.models.research.object_detection.utils import ops as utils_ops


class ObjectDetect:
    @staticmethod
    def add_args(parser: argparse.ArgumentParser):
        parser.add_argument("--obj_det_model_name", default='ssd_mobilenet_v1_coco_2017_11_17')
        parser.add_argument('--obj_det_labels', default='object_detection/data/mscoco_label_map.pbtxt')

    def __init__(
            self,
            args):
        model_name = args.obj_det_model_name
        PATH_TO_LABELS = args.obj_det_labels
        self.model_name = model_name
        base_url = 'http://download.tensorflow.org/models/object_detection/'
        model_file = model_name + '.tar.gz'
        model_dir = tf.keras.utils.get_file(
            fname=model_name,
            origin=base_url + model_file,
            untar=True)

        model_dir = pathlib.Path(model_dir) / "saved_model"

        self.model = tf.saved_model.load(str(model_dir))
        self.model = self.model.signatures['serving_default']
        self.PATH_TO_LABELS = PATH_TO_LABELS

        self.translater = ['человек', 'велосипед', 'машина', 'мотоцикл', 'самолет', 'автобус', 'поезд', 'грузовик', 'лодка',
                      'светофор', 'пожарный кран', '', 'знак остановки', 'паркомат', 'скамейка', 'птица',
                      'кот', 'собака', 'лошадь', 'овца', 'корова', ' слон', 'медведь', 'зебра', 'жираф', '', 'рюкзак',
                      'зонт', '', '', 'сумочка', 'галстук', 'чемодан', 'фрисби', 'лыжи', 'сноуборд', 'спортивный мяч',
                      'воздушный змей', 'бейсбольная бита', 'бейсбольная перчатка', 'скейтборд', 'доска для серфинга',
                      'тенисна ракетка', 'бутылка', '', 'бокал для вина', 'чашка', 'вилка', 'нож',
                      'ложка', 'чаша', 'банан', 'яблоко', 'бутерброд', 'апельсин', 'брокколи', 'морковь', 'хот-дог',
                      'пицца', 'пончик', 'торт', 'стул', 'диван', 'растение в горшке', 'кровать', '',
                      'обеденный стол', '', '', 'туалет', '', 'телевизор', 'ноутбук', 'мышь', 'удаленный', 'клавиатура',
                      'мобильный телефон', 'микроволновая печь', 'духовой шкаф', 'тостер', 'раковина', 'холодильник',
                      '', 'книга', 'часы', 'ваза', 'ножницы', 'плюшевый мишка', 'фен', 'зубная щетка']

    def run_inference_for_single_image(self, image):
        image = np.asarray(image)
        input_tensor = tf.convert_to_tensor(image)
        input_tensor = input_tensor[tf.newaxis, ...]
        output_dict = self.model(input_tensor)
        num_detections = int(output_dict.pop('num_detections'))
        output_dict = {key: value[0, :num_detections].numpy()
                       for key, value in output_dict.items()}
        output_dict['num_detections'] = num_detections
        output_dict['detection_classes'] = output_dict['detection_classes'].astype(np.int64)

        if 'detection_masks' in output_dict:
            detection_masks_reframed = utils_ops.reframe_box_masks_to_image_masks(
                output_dict['detection_masks'], output_dict['detection_boxes'],
                image.shape[0], image.shape[1])
            detection_masks_reframed = tf.cast(detection_masks_reframed > 0.5,
                                               tf.uint8)
            output_dict['detection_masks_reframed'] = detection_masks_reframed.numpy()
        return output_dict

    def show_inference(self, img):
        image_np = np.array(img)
        output_dict = self.run_inference_for_single_image(image_np)
        objects_on_image = []
        for i, x in enumerate(output_dict['detection_classes']):
            if output_dict['detection_scores'][i] > 0.5:
                objects_on_image.append(x)
        return objects_on_image

    def get_objects_from_image(self, img):
        a = self.show_inference(img)
        names = []
        for i in range(len(a)):
            names.append(self.translater[a[i] - 1])
        return names


def main():
    parser = argparse.ArgumentParser()
    ObjectDetect.add_args(parser)
    args = parser.parse_args()
    detector = ObjectDetect(args)

    TEST_IMAGE_PATHS = ['modules/object_detect/tuta.jpg']
    for image_path in TEST_IMAGE_PATHS:
        img = Image.open(image_path)
        names = detector.get_objects_from_image(img)
        print(image_path, names)


if __name__ == "__main__":
    main()
