from ultralytics import YOLO
import numpy as np
import onnxruntime as ort
import cv2
import pyttsx3
import threading

# Load once
yolo_model = YOLO(r"detection\models\yolov8n.pt")  # Replace with your path

onnx_model_path = r"detection\models\Depth_Anything_Metric_V2.ort"
session = ort.InferenceSession(
    onnx_model_path,
    providers=['CUDAExecutionProvider', 'CPUExecutionProvider']
)

input_name = session.get_inputs()[0].name
output_name = session.get_outputs()[0].name

def preprocess_image(image, target_size=(1280, 720)):
    """
    Preprocess image for depth model.
    image: OpenCV BGR image (numpy array)
    """
    original_shape = image.shape[:2]  # (height, width)
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    image_resized = cv2.resize(image_rgb, target_size)
    image_norm = image_resized.astype(np.float32) / 255.0
    image_chw = np.transpose(image_norm, (2, 0, 1))  # CHW
    input_tensor = np.expand_dims(image_chw, axis=0)  # batch dimension
    return input_tensor, original_shape


def detect_objects(image):
    results = yolo_model(image)
    objects = []
    for box in results[0].boxes:
        cls_id = int(box.cls[0])
        conf = float(box.conf[0])
        objects.append({
            "class": results[0].names[cls_id],
            "confidence": round(conf, 2)
        })
    return objects

def detect_and_draw(image):
    results = yolo_model(image)
    return results[0].plot()

# Assuming you already have your YOLO model loaded as yolo_model

def depth_map_to_image(depth_map):
    # Normalize depth map to [0, 255]
    depth_min = np.min(depth_map)
    depth_max = np.max(depth_map)
    depth_normalized = (depth_map - depth_min) / (depth_max - depth_min + 1e-6)  # avoid div0
    depth_8bit = (depth_normalized * 255).astype(np.uint8)
    return depth_8bit

def depth_map_to_colormap(depth_map):
    depth_8bit = depth_map_to_image(depth_map)
    depth_color = cv2.applyColorMap(depth_8bit, cv2.COLORMAP_JET)
    return depth_color

def speak(text):
    def _speak():
        import pythoncom
        pythoncom.CoInitialize() 
        engine = pyttsx3.init()
        engine.say(text)
        engine.runAndWait()
    threading.Thread(target=_speak).start()

def detect_and_estimate_depth(image):
    try:
        results = yolo_model(image)

        input_tensor, original_shape = preprocess_image(image)
        print('all threee done')

        outputs = session.run([output_name], {input_name: input_tensor})
        depth_map = outputs[0].squeeze()*0.5

        depth_h, depth_w = depth_map.shape
        orig_h, orig_w = original_shape
        scale_x = depth_w / orig_w
        scale_y = depth_h / orig_h

        # spoken_objects = [] 

        for result in results:
            for box in result.boxes:
                x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())
                class_id = int(box.cls[0])
                class_name = yolo_model.names[class_id]

                cx = int((x1 + x2) / 2 * scale_x)
                cy = int((y1 + y2) / 2 * scale_y)
                cx = np.clip(cx, 0, depth_w - 1)
                cy = np.clip(cy, 0, depth_h - 1)

                depth_value = depth_map[cy, cx]

                label = f"{class_name}: {depth_value:.2f}m"
                cv2.rectangle(image, (x1, y1), (x2, y2), (255, 0, 0), 2)
                cv2.putText(image, label, (x1, y1 - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)
                # if class_name not in spoken_objects:
                    # spoken_objects.append(class_name)
                speak(f"{class_name} at {depth_value:.2f} meters")

        depth_map = depth_map_to_colormap(depth_map)
        return depth_map, image

   
    except Exception as e:
        print("Error in detect_and_estimate_depth:", e)
