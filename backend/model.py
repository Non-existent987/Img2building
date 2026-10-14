"""建筑物识别模型加载与推理。

模型结构：segmentation-models-pytorch的 Unet + EfficientNet-B4 编码器
权重文件：Lightning checkpoint，外层包了 best_model/，内部为 model_state_dict
"""

import pathlib

import numpy as np
import torch

ROOT = pathlib.Path(__file__).resolve().parent.parent
MODEL_DIR = ROOT / "frontend" / "model" / "Identification_model_file"
MODEL_PATH = MODEL_DIR / "img2building_model.pth"

# 分割头输出通道数：由权重 shape 确认是 1（单通道 sigmoid 语义）
# 建筑物提取是二值任务，1 类 + sigmoid 比 2 类 softmax 更贴合
NUM_CLASSES = 1
IN_CHANNELS = 3
ENCODER = "efficientnet-b4"

_device = "cuda" if torch.cuda.is_available() else "cpu"
_model = None


def _build_model():
    import segmentation_models_pytorch as smp

    model = smp.Unet(
        encoder_name=ENCODER,
        encoder_weights=None,
        in_channels=IN_CHANNELS,
        classes=NUM_CLASSES,
    )
    return model


def load_model():
    """加载权重，进程内缓存。失败返回 None 而不抛出，保证服务可启动。"""
    global _model
    if _model is not None:
        return _model

    if not MODEL_PATH.is_file():
        print(f"[warn] 未找到模型文件: {MODEL_PATH}")
        print("[warn] 请将 img2building_model.pth 放入 frontend/model/Identification_model_file/")
        return None

    try:
        ckpt = torch.load(MODEL_PATH, map_location="cpu", weights_only=False)
        # Lightning ckpt 外层是 dict，权重在 model_state_dict
        state = ckpt.get("model_state_dict", ckpt) if isinstance(ckpt, dict) else ckpt
        # 去掉可能的 module. 前缀
        state = {k[7:] if k.startswith("module.") else k: v for k, v in state.items()}

        model = _build_model()
        model.load_state_dict(state, strict=True)
        model.eval()
        model.to(_device)
        _model = model
        print(f"[ok] 模型已加载 ({ENCODER}/Unet, {NUM_CLASSES}类) 设备={_device}")
        return _model
    except Exception as e:
        print(f"[error] 模型加载失败: {e}")
        return None


def model_ready() -> bool:
    return load_model() is not None


def device() -> str:
    return _device


@torch.no_grad()
def predict_mask(tile: np.ndarray) -> np.ndarray:
    """对单块影像推理。

    tile: HWC uint8 RGB
    返回: HW uint8二值掩膜，1=建筑物
    """
    model = load_model()
    if model is None:
        return np.zeros(tile.shape[:2], dtype=np.uint8)

    # HWC uint8 -> CHW float32 归一化
    x = torch.from_numpy(tile).permute(2, 0, 1).float() / 255.0
    x = x.unsqueeze(0).to(_device)

    logits = model(x)
    prob = torch.sigmoid(logits)[0, 0]   # 单通道输出

    mask = (prob.cpu().numpy() > 0.5).astype(np.uint8)
    return mask


@torch.no_grad()
def prob_map(tile: np.ndarray) -> np.ndarray:
    """返回建筑物概率图float32，取值0~1。"""
    model = load_model()
    if model is None:
        return np.zeros(tile.shape[:2], dtype=np.float32)

    x = torch.from_numpy(tile).permute(2, 0, 1).float() / 255.0
    x = x.unsqueeze(0).to(_device)

    logits = model(x)
    prob = torch.sigmoid(logits)[0, 0]
    return prob.cpu().numpy().astype(np.float32)