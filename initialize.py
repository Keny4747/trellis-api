#!/usr/bin/env python3
import os
import sys
import argparse
import imageio
from PIL import Image
import time
from trellis.pipelines import TrellisImageTo3DPipeline
from trellis.utils import render_utils, postprocessing_utils

def initialize_models():
    print("Initialize TRELLIS pipeline...")
    pipeline = TrellisImageTo3DPipeline.from_pretrained("JeffreyXiang/TRELLIS-image-large")
    print("TRELLIS Pipeline loaded successfully")
    
if __name__ == "__main__":
    initialize_models()