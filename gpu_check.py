# GPU 동작 확인 스크립트
import torch

print("PyTorch:", torch.__version__)
print("CUDA Runtime (PyTorch):", torch.version.cuda)
print("CUDA available:", torch.cuda.is_available())

if torch.cuda.is_available():
    print("GPU:", torch.cuda.get_device_name(0))
    print("GPU Memory:", torch.cuda.get_device_properties(0).total_memory / 1024**3, "GB")
    print("CUDA Capability:", torch.cuda.get_device_capability(0))
else:
    print("❌ CUDA를 사용할 수 없습니다!")

