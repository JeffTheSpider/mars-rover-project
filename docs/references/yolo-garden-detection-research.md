# YOLO Garden Object Detection Research

**Date**: 2026-03-15
**Source**: Research agent — Ultralytics docs, Seeed Studio benchmarks, NVIDIA forums, community guides

## 1. Pre-trained YOLOv8n COCO Classes (Garden-Relevant)

YOLOv8n detects 80 COCO classes out of the box. Garden-relevant subset:

| Category | Classes |
|----------|---------|
| Living things | person, dog, cat, bird, horse, sheep, cow |
| Vehicles | bicycle, car, motorcycle, bus, truck |
| Outdoor objects | bench, fire hydrant, parking meter, stop sign |
| Plants/food | potted plant, apple, orange, banana |
| Furniture | chair, dining table, couch |
| Items | backpack, umbrella, handbag, suitcase |
| Sports | frisbee, sports ball, kite, skateboard |

## 2. Custom Garden Objects NOT in COCO

**High priority** (common obstacles): garden hose, sprinkler, wheelbarrow, garden tools (fork/spade/rake), lawnmower, compost bin, watering can, garden ornaments, trampoline, shed, fence/gate, stepping stones.

**Medium priority** (navigation): lawn edge, tree trunk/stump, pond, BBQ, patio furniture (parasol, sun lounger), greenhouse, bird feeder/bath, terracotta pots, weed patches.

## 3. Transfer Learning

### Images per class
- **Minimum viable**: 100-300 images/class (works but lower accuracy)
- **Good results**: 500-1,000 images/class
- **Optimal**: 1,500+ images/class (Ultralytics recommendation)
- Use heavy data augmentation (rotation, flip, brightness, blur, crop, mosaic)

### Keeping COCO classes while adding custom ones

**Approach A: Mixed dataset (recommended)**
1. Create custom garden dataset with new class annotations
2. Mix in representative subset of COCO images (garden-relevant classes)
3. Train with all classes (80 COCO + N custom)
4. Lower learning rate (`lr0=0.001`) and freeze backbone (`freeze=10`)

```bash
yolo detect train model=yolov8n.pt data=garden_mixed.yaml epochs=100 imgsz=640 batch=16 lr0=0.001 freeze=10
```

**Approach B: Two-model pipeline** (simplest)
- Stock YOLOv8n for COCO classes + separate custom model for garden classes
- Merge detections in post-processing
- Doubles compute cost but easiest to maintain

## 4. TensorRT Export

**MUST export ON the Jetson** — engines are GPU-architecture-specific.

```bash
# Direct export
yolo export model=yolov8n.pt format=engine half=True device=0 imgsz=640

# Two-step (more control)
yolo export model=yolov8n.pt format=onnx imgsz=640 simplify=True opset=18
/usr/src/tensorrt/bin/trtexec --onnx=yolov8n.onnx --saveEngine=yolov8n_fp16.engine --fp16
```

**Gotchas:**
- FP16 + dynamic shapes incompatible — use static input size
- Export on Jetson, not PC (GPU architecture mismatch)
- Match Ultralytics pip version with JetPack TensorRT/CUDA versions

## 5. Performance on Jetson Orin Nano Super (67 TOPS)

| Resolution | FP16 FPS | INT8 FPS | Notes |
|-----------|----------|----------|-------|
| 640x640 | ~25-35 | ~50-65 | Best detection quality |
| 416x416 | ~60-80 | ~100+ | Good compromise |
| 320x320 | ~80-120 | ~130+ | Small object detection suffers |

- Enable `jetson_clocks` and MAXN power mode for best performance
- 30+ FPS at 640x640 is plenty for garden robot at walking speed (~5 km/h)

## 6. Depth Integration: YOLO + OAK-D for 3D Obstacles

### Recommended combined pipeline

1. OAK-D publishes synchronized RGB + depth via `depthai-ros`
2. Jetson runs YOLOv8n TensorRT on RGB at ~30 FPS
3. Custom ROS2 node fuses YOLO 2D boxes with depth → `Detection3DArray`
4. Raw depth pointcloud feeds Nav2 voxel costmap (geometric obstacle avoidance)
5. YOLO detections feed semantic costmap layer (different costs per object type)
6. Nav2 planner uses combined costmap

### Nav2 costmap config for depth pointcloud

```yaml
local_costmap:
  plugins: ["voxel_layer", "inflation_layer"]
  voxel_layer:
    plugin: "nav2_costmap_2d::VoxelLayer"
    observation_sources: oakd_depth
    oakd_depth:
      topic: /oakd/pointcloud
      data_type: PointCloud2
      marking: true
      clearing: true
      max_obstacle_height: 2.0
      min_obstacle_height: 0.05
```

## Sources

- [Ultralytics COCO Dataset](https://docs.ultralytics.com/datasets/detect/coco/)
- [Ultralytics TensorRT Export](https://docs.ultralytics.com/integrations/tensorrt/)
- [Seeed Studio YOLOv8 Benchmarks on Jetson](https://www.seeedstudio.com/blog/2023/03/30/yolov8-performance-benchmarks-on-nvidia-jetson-devices/)
- [Extending YOLOv8 With New Classes](https://y-t-g.github.io/tutorials/yolov8n-add-classes/)
- [Ultralytics Training Tips](https://docs.ultralytics.com/yolov5/tutorials/tips_for_best_training_results/)
- [DepthAI ROS Driver](https://github.com/luxonis/depthai-ros)
- [Nav2 Sensor Setup](https://navigation.ros.org/setup_guides/sensors/setup_sensors.html)
- [NVIDIA Orin Nano Super](https://blogs.nvidia.com/blog/jetson-generative-ai-supercomputer/)
