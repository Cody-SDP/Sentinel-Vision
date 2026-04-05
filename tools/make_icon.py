from PIL import Image
import os

def generate_icon(input_path, output_name="Sentinel-Vision.ico"):
    if not os.path.exists(input_path):
        print(f"❌ File not found: {input_path}")
        return

    img = Image.open(input_path)

    from PIL import Image
import os

def generate_icon(input_path, output_path):
    if not os.path.exists(input_path):
        print(f"❌ File not found: {input_path}")
        return

    img = Image.open(input_path)

    width, height = img.size
    min_dim = min(width, height)

    left = (width - min_dim) // 2
    top = (height - min_dim) // 2
    right = left + min_dim
    bottom = top + min_dim

    cropped = img.crop((left, top, right, bottom))

    sizes = [(16,16), (32,32), (48,48), (64,64), (128,128), (256,256)]
    cropped.save(output_path, format="ICO", sizes=sizes)

    print(f"✅ Icon created: {output_path}")

if __name__ == "__main__":
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    input_file = os.path.join(project_root, "assets", "logo_raw.png")
    output_file = os.path.join(project_root, "assets", "Sentinel-Vision-new.ico")

    generate_icon(input_file, output_file)