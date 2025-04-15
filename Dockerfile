# Use CUDA base image
FROM nvidia/cuda:11.8.0-cudnn8-devel-ubuntu22.04

# Set environment variables
ENV DEBIAN_FRONTEND=noninteractive
ENV CUDA_HOME=/usr/local/cuda
ENV PATH=${CUDA_HOME}/bin:${PATH}
ENV LD_LIBRARY_PATH=${CUDA_HOME}/lib64:${LD_LIBRARY_PATH}
# Set CUDA architecture flags
ENV TORCH_CUDA_ARCH_LIST="7.0;7.5;8.0;8.6+PTX"
ENV FORCE_CUDA=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    python3.10 \
    python3.10-dev \
    python3-pip \
    wget \
    git \
    ninja-build \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Set Python 3.10 as default
RUN update-alternatives --install /usr/bin/python python /usr/bin/python3.10 1 && \
    update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.10 1

# Upgrade pip
RUN python -m pip install --upgrade pip setuptools wheel

# Create workspace and clone repository
WORKDIR /workspace
RUN git clone --recurse-submodules https://github.com/microsoft/TRELLIS.git && \
    cd TRELLIS

# Install PyTorch
RUN pip install torch==2.4.0 torchvision==0.19.0 --index-url https://download.pytorch.org/whl/cu118

# Verify CUDA installation and paths
RUN nvcc --version && \
    python -c "import torch; print('CUDA available:', torch.cuda.is_available())"

# Install basic dependencies
RUN pip install pillow imageio imageio-ffmpeg tqdm easydict opencv-python-headless \
    scipy ninja rembg onnxruntime trimesh xatlas pyvista pymeshfix igraph transformers && \
    pip install git+https://github.com/EasternJournalist/utils3d.git@9a4eb15e4021b67b12c460c7057d642626897ec8

# Install xformers
RUN pip install xformers==0.0.27.post2 --index-url https://download.pytorch.org/whl/cu118

# Install flash-attention
RUN pip install flash-attn

# Install kaolin
RUN pip install kaolin -f https://nvidia-kaolin.s3.us-east-2.amazonaws.com/torch-2.4.0_cu121.html

# Install nvdiffrast
RUN mkdir -p /tmp/extensions && \
    git clone https://github.com/NVlabs/nvdiffrast.git /tmp/extensions/nvdiffrast && \
    pip install /tmp/extensions/nvdiffrast

# Install diffoctreerast
RUN mkdir -p /tmp/extensions && \
    git clone --recurse-submodules https://github.com/JeffreyXiang/diffoctreerast.git /tmp/extensions/diffoctreerast && \
    pip install /tmp/extensions/diffoctreerast

# Install mip-splatting
RUN mkdir -p /tmp/extensions && \
    git clone https://github.com/autonomousvision/mip-splatting.git /tmp/extensions/mip-splatting && \
    pip install /tmp/extensions/mip-splatting/submodules/diff-gaussian-rasterization/

# Install spconv
RUN pip install spconv-cu118

# Install demo dependencies
RUN pip install gradio==4.44.1 gradio_litmodel3d==0.0.1

RUN pip install flask-cors

# Set working directory
WORKDIR /workspace/TRELLIS

# Create input and output directories
RUN mkdir -p /workspace/TRELLIS/input /workspace/TRELLIS/output

# Install Flask for the service
RUN pip install flask requests

# Copy the Python scripts
COPY service.py /workspace/TRELLIS/service.py
COPY process.py /workspace/TRELLIS/process.py
COPY initialize.py /workspace/TRELLIS/initialize.py
RUN chmod +x /workspace/TRELLIS/service.py /workspace/TRELLIS/process.py /workspace/TRELLIS/initialize.py

# Expose the port
EXPOSE 5000

# Set the entrypoint to run the service
CMD ["python", "service.py"]
