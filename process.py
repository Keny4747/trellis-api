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
    
def process_image(input_path, output_dir):
    """Process a single image with TRELLIS"""
    print(f"\nStarting TRELLIS processing pipeline...")
    
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)

    # Set SPCONV_ALGO
    os.environ['SPCONV_ALGO'] = 'native'

    print("Loading TRELLIS pipeline...")
    # Load the pipeline
    pipeline = TrellisImageTo3DPipeline.from_pretrained("JeffreyXiang/TRELLIS-image-large")
    pipeline.cuda()
    print("Pipeline loaded and moved to CUDA successfully")

    # Load the image
    print(f"Loading input image: {input_path}")
    image = Image.open(input_path)
    print(f"Image loaded successfully. Size: {image.size}")

    # Run the pipeline
    print("\nRunning TRELLIS pipeline (this may take several minutes)...")
    start_time = time.time()
    outputs = pipeline.run(image, seed=1)
    processing_time = time.time() - start_time
    print(f"Pipeline processing completed in {processing_time:.2f} seconds")

    # Save outputs
    print("\nSaving output files...")
    
    print("Rendering and saving gaussian video...")
    video = render_utils.render_video(outputs['gaussian'][0])['color']
    imageio.mimsave(os.path.join(output_dir, "output_gaussian.mp4"), video, fps=30)
    
    print("Rendering and saving radiance field video...")
    video = render_utils.render_video(outputs['radiance_field'][0])['color']
    imageio.mimsave(os.path.join(output_dir, "output_radiance.mp4"), video, fps=30)
    
    print("Rendering and saving mesh video...")
    video = render_utils.render_video(outputs['mesh'][0])['normal']
    imageio.mimsave(os.path.join(output_dir, "output_mesh.mp4"), video, fps=30)

    print("Generating and saving GLB file...")
    glb = postprocessing_utils.to_glb(
        outputs['gaussian'][0],
        outputs['mesh'][0],
        simplify=0.0,
        texture_size=1024,
    )
    glb.export(os.path.join(output_dir, "output.glb"))

    print(f"\nProcessing complete! All files saved to: {output_dir}")
    return {
        'gaussian': "output_gaussian.mp4",
        'radiance': "output_radiance.mp4",
        'mesh': "output_mesh.mp4",
        'glb': "output.glb"
    }

def main():
    parser = argparse.ArgumentParser(description='Process image with TRELLIS')
    parser.add_argument('input_image', help='Path to the input image')
    parser.add_argument('output_dir', help='Directory for output files')
    args = parser.parse_args()
    
    process_image(args.input_image, args.output_dir)

if __name__ == "__main__":
    main()