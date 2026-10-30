from pathlib import Path
from huggingface_hub import hf_hub_download

ROOT = Path(__file__).resolve().parent
MODEL_DIR = ROOT / "model"
MODEL_DIR.mkdir(exist_ok=True)

path = hf_hub_download(
    repo_id="cosgun99/gun-knife-yolo11n",
    filename="best.pt",
    local_dir=str(MODEL_DIR),
)
print(f"Model downloaded to: {path}")
