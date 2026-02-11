from PIL import Image
import os

SOURCE_IMAGE = 'app-icon.png'
SIZES = {
    'icon-192.png': (192, 192),
    'icon-512.png': (512, 512),
    'apple-touch-icon.png': (180, 180),  # specific size for iOS
    'favicon.ico': (32, 32)
}

def generate_icons():
    if not os.path.exists(SOURCE_IMAGE):
        print(f"Error: {SOURCE_IMAGE} not found.")
        return

    try:
        img = Image.open(SOURCE_IMAGE)
        # Ensure image is square by cropping or resizing appropriately
        # Assuming user provided a square-ish image, but let's just resize for now
        # Better: resize and center crop if not square?
        # For simplicity, resize with resampling.
        
        for filename, size in SIZES.items():
            # high quality resizing
            new_img = img.resize(size, Image.Resampling.LANCZOS)
            new_img.save(filename)
            print(f"Generated {filename} ({size[0]}x{size[1]})")

    except Exception as e:
        print(f"Error processing image: {e}")

if __name__ == "__main__":
    generate_icons()
