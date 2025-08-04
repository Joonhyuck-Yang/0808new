#!/usr/bin/env python3
"""
GPU Test Script
Comprehensive GPU testing for machine learning workloads
"""

import time
import torch
import torch.nn as nn

def test_gpu_performance():
    """Test GPU performance with a simple neural network"""
    print("🚀 Testing GPU performance...")
    
    if not torch.cuda.is_available():
        print("❌ GPU not available")
        return
        
    device = torch.device('cuda')
    print(f"✅ Using device: {device}")
    
    # Create a simple neural network
    model = nn.Sequential(
        nn.Linear(1000, 500),
        nn.ReLU(),
        nn.Linear(500, 100),
        nn.ReLU(),
        nn.Linear(100, 10)
    ).to(device)
    
    # Create test data
    batch_size = 64
    x = torch.randn(batch_size, 1000).to(device)
    y = torch.randint(0, 10, (batch_size,)).to(device)
    
    # Test forward pass
    start_time = time.time()
    for _ in range(100):
        output = model(x)
    forward_time = time.time() - start_time
    
    print(f"✅ Forward pass time: {forward_time:.4f}s")
    
    # Test backward pass
    criterion = nn.CrossEntropyLoss()
    optimizer = torch.optim.Adam(model.parameters())
    
    start_time = time.time()
    for _ in range(100):
        optimizer.zero_grad()
        output = model(x)
        loss = criterion(output, y)
        loss.backward()
        optimizer.step()
    backward_time = time.time() - start_time
    
    print(f"✅ Backward pass time: {backward_time:.4f}s")
    print(f"✅ Total training time: {forward_time + backward_time:.4f}s")

if __name__ == "__main__":
    test_gpu_performance() 