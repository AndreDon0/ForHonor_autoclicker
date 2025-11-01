#!/usr/bin/env python
"""
train_yolo_windows.py

Usage (from your venv):
    python train_yolo_windows.py --data_dir data --out_dir data_split --val_ratio 0.2 --epochs 50

What it does:
 - Reads classes from data/classes.txt (one class name per line)
 - Collects image files from data/images and matching label files from data/labels
 - Splits dataset into train/val (random seedable)
 - Copies files into out_dir/images/{train,val} and out_dir/labels/{train,val}
 - Writes out out_dir/data.yaml suitable for ultralytics YOLO
 - Calls ultralytics.YOLO(...) to train and copies best.pt to out_dir/best.pt
"""
import argparse
import shutil
from pathlib import Path
import random
import yaml
import sys
import os
import torch

def read_classes(classes_path: Path):
    if classes_path.exists():
        with classes_path.open('r', encoding='utf-8') as f:
            names = [line.strip() for line in f.readlines() if line.strip()]
            if len(names) > 0:
                return names
    return None

def collect_pairs(images_dir: Path, labels_dir: Path):
    imgs = sorted([p for p in images_dir.iterdir() if p.is_file() and p.suffix.lower() in ('.jpg','.jpeg','.png')])
    pairs = []
    for im in imgs:
        lbl = labels_dir / (im.stem + '.txt')
        if lbl.exists():
            pairs.append((im, lbl))
        else:
            # skip images without label (YOLO requires labels)
            pass
    return pairs

def copy_split(pairs, out_dir: Path, val_ratio=0.2, seed=42):
    random.seed(seed)
    random.shuffle(pairs)
    n = len(pairs)
    n_val = max(1, int(n * val_ratio))
    val_pairs = pairs[:n_val]
    train_pairs = pairs[n_val:]

    for subset_name, subset in (('train', train_pairs), ('val', val_pairs)):
        img_out = out_dir / 'images' / subset_name
        lbl_out = out_dir / 'labels' / subset_name
        img_out.mkdir(parents=True, exist_ok=True)
        lbl_out.mkdir(parents=True, exist_ok=True)
        for im, lb in subset:
            shutil.copy2(im, img_out / im.name)
            shutil.copy2(lb, lbl_out / lb.name)
    return len(train_pairs), len(val_pairs)

def write_data_yaml(out_dir: Path, names):
    d = {
        'path': str(out_dir.resolve()),
        'train': 'images/train',
        'val': 'images/val',
        'nc': len(names),
        'names': names
    }
    p = out_dir / 'data.yaml'
    with p.open('w', encoding='utf-8') as f:
        yaml.dump(d, f, sort_keys=False, allow_unicode=True)
    return p

def train_with_ultralytics(data_yaml_path: Path, model_ckpt: str, epochs:int, imgsz:int, batch:int, run_name:str, out_dir:Path):
    try:
        from ultralytics import YOLO
    except Exception as e:
        print("ERROR: ultralytics not installed in this environment. Install it in your venv and re-run:")
        print("  pip install ultralytics")
        raise
    
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    print(f"Using device: {device}")

    print(f"Starting training with model {model_ckpt}, epochs={epochs}, imgsz={imgsz}, batch={batch}")
    model = YOLO(model_ckpt)
    results = model.train(data=str(data_yaml_path), epochs=epochs, imgsz=imgsz, batch=batch, name=run_name, device=device)
    # ultralytics saves runs to ./runs/detect/<run_name> or runs/segment for segmentation
    # Try to find best.pt and copy to out_dir
    runs_dir = Path('runs')
    best_found = False
    if runs_dir.exists():
        for p in runs_dir.rglob('best.pt'):
            try:
                target = out_dir / 'best.pt'
                shutil.copy2(p, target)
                print("Copied best.pt to", target)
                best_found = True
                break
            except Exception as e:
                print("Failed to copy best.pt:", e)
    if not best_found:
        print("No best.pt found in runs. Check the runs/ directory for saved weights.")
    return results

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--data_dir', type=str, default='data', help='Root dataset folder containing images/ and labels/ and classes.txt')
    parser.add_argument('--out_dir', type=str, default='data_split', help='Output dataset folder for train/val split and data.yaml')
    parser.add_argument('--val_ratio', type=float, default=0.2)
    parser.add_argument('--seed', type=int, default=42)
    parser.add_argument('--model', type=str, default='yolov8n.pt', help='YOLOv8 pretrained checkpoint to start from (yolov8n.pt/yolov8s.pt/etc)')
    parser.add_argument('--epochs', type=int, default=100)
    parser.add_argument('--imgsz', type=int, default=640)
    parser.add_argument('--batch', type=int, default=16)
    parser.add_argument('--run_name', type=str, default='forhonor_train')
    parser.add_argument('--export', action='store_true', help='Export final model to ONNX after training (requires ultralytics export support)')
    args = parser.parse_args()

    data_dir = Path(args.data_dir)
    images_dir = data_dir / 'images'
    labels_dir = data_dir / 'labels'
    classes_file = data_dir / 'classes.txt'

    if not images_dir.exists() or not labels_dir.exists():
        print("ERROR: expected directories missing. Check that you have:")
        print("  data/images  and  data/labels")
        sys.exit(1)

    names = read_classes(classes_file)
    if names is None:
        print("WARNING: classes.txt not found or empty. Attempting to infer classes from label files.")
        # attempt inference
        max_cls = -1
        for lf in labels_dir.glob('*.txt'):
            for line in lf.read_text(encoding='utf-8').splitlines():
                if not line.strip(): continue
                try:
                    cls = int(float(line.split()[0]))
                    if cls > max_cls: max_cls = cls
                except Exception:
                    continue
        if max_cls >= 0:
            names = [f'class{i}' for i in range(max_cls+1)]
            print("Inferred class count:", len(names))
        else:
            names = ['class0']  # fallback
            print("Falling back to single class 'class0'")

    pairs = collect_pairs(images_dir, labels_dir)
    if len(pairs) == 0:
        print("No image+label pairs were found. Exiting.")
        sys.exit(1)

    out_dir = Path(args.out_dir)
    if out_dir.exists():
        print(f"Output directory {out_dir} already exists; files may be overwritten.")
    out_dir.mkdir(parents=True, exist_ok=True)

    n_train, n_val = copy_split(pairs, out_dir, val_ratio=args.val_ratio, seed=args.seed)
    print(f"Copied {n_train} train and {n_val} val samples into {out_dir}")

    data_yaml_path = write_data_yaml(out_dir, names)
    print("Wrote data.yaml to", data_yaml_path)

    # Attempt training (requires ultralytics installed)
    try:
        res = train_with_ultralytics(data_yaml_path, args.model, args.epochs, args.imgsz, args.batch, args.run_name, out_dir)
        print("Training finished. Check ./runs for detailed logs and metrics.")
        if args.export:
            try:
                from ultralytics import YOLO
                model = YOLO(str(out_dir / 'best.pt')) if (out_dir / 'best.pt').exists() else YOLO(args.model)
                print("Exporting model to ONNX (this may require additional packages).")
                model.export(format='onnx')
                print("Export complete.")
            except Exception as e:
                print("Export failed:", e)
    except Exception as e:
        print("Training aborted:", e)
        print("If ultralytics isn't installed in your venv, install it with:")
        print("  pip install ultralytics")
        sys.exit(1)

if __name__ == '__main__':
    main()
