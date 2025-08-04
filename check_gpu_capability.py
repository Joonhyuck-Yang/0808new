#!/usr/bin/env python3
"""
GPU Capability Check Script
Check if GPU is available and working properly
"""

import sys
import subprocess

def check_gpu():
    """Check GPU availability and capabilities"""
    print("🔍 Checking GPU capabilities...")
    
    try:
        # Check if CUDA is available
        import torch
        if torch.cuda.is_available():
            print("✅ CUDA is available")
            print(f"   GPU Count: {torch.cuda.device_count()}")
            for i in range(torch.cuda.device_count()):
                print(f"   GPU {i}: {torch.cuda.get_device_name(i)}")
        else:
            print("❌ CUDA is not available")
            
    except ImportError:
        print("❌ PyTorch is not installed")
        
    try:
        # Check nvidia-smi
        result = subprocess.run(['nvidia-smi'], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ nvidia-smi is working")
            print(result.stdout)
        else:
            print("❌ nvidia-smi failed")
            
    except FileNotFoundError:
        print("❌ nvidia-smi not found")

if __name__ == "__main__":
    check_gpu() 