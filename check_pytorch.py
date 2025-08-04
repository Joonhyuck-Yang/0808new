#!/usr/bin/env python3
"""
PyTorch Installation Check Script
Verify PyTorch installation and version
"""

def check_pytorch():
    """Check PyTorch installation and capabilities"""
    print("🔍 Checking PyTorch installation...")
    
    try:
        import torch
        print(f"✅ PyTorch version: {torch.__version__}")
        
        # Check CUDA support
        if torch.cuda.is_available():
            print(f"✅ CUDA version: {torch.version.cuda}")
            print(f"✅ cuDNN version: {torch.backends.cudnn.version()}")
        else:
            print("❌ CUDA not available")
            
        # Test basic operations
        x = torch.randn(3, 3)
        y = torch.randn(3, 3)
        z = torch.mm(x, y)
        print("✅ Basic tensor operations working")
        
        # Test GPU if available
        if torch.cuda.is_available():
            x_gpu = x.cuda()
            y_gpu = y.cuda()
            z_gpu = torch.mm(x_gpu, y_gpu)
            print("✅ GPU tensor operations working")
            
    except ImportError as e:
        print(f"❌ PyTorch not installed: {e}")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    check_pytorch() 