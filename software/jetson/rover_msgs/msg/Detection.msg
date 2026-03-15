# Object detection result from YOLO inference
string class_name
float32 confidence
int32[4] bbox        # x, y, width, height (pixels)
float32 distance     # estimated distance in metres (-1.0 if unavailable)
