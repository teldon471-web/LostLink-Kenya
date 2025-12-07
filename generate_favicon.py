#!/usr/bin/env python
"""
Favicon Generator for LostLink Kenya
Converts SVG designs to PNG and ICO formats
"""

import os
import sys
from pathlib import Path

def generate_favicon_with_cairosvg():
    """Generate PNG favicon using cairosvg library"""
    try:
        import cairosvg
        from PIL import Image
        
        # Directory paths
        project_root = Path(__file__).parent
        static_dir = project_root / "blog" / "static"
        static_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate PNG from SVG (recommended: favicon-alt.svg)
        svg_file = project_root / "favicon-alt.svg"
        png_file = static_dir / "favicon.png"
        ico_file = static_dir / "favicon.ico"
        
        print(f"📁 Source SVG: {svg_file}")
        print(f"📁 Output PNG: {png_file}")
        print(f"📁 Output ICO: {ico_file}")
        
        # Convert SVG to PNG (32x32 and 256x256)
        print("\n🔄 Converting SVG to PNG (256x256)...")
        cairosvg.svg2png(
            url=str(svg_file),
            write_to=str(png_file),
            output_width=256,
            output_height=256
        )
        print("✅ PNG created: favicon.png (256x256)")
        
        # Also create 32x32 version
        png_32_file = static_dir / "favicon-32x32.png"
        print("🔄 Converting SVG to PNG (32x32)...")
        cairosvg.svg2png(
            url=str(svg_file),
            write_to=str(png_32_file),
            output_width=32,
            output_height=32
        )
        print("✅ PNG created: favicon-32x32.png (32x32)")
        
        # Create ICO from PNG
        print("🔄 Converting PNG to ICO...")
        img = Image.open(png_file)
        ico_sizes = [(256, 256), (128, 128), (64, 64), (48, 48), (32, 32), (16, 16)]
        img.save(ico_file, format='ICO', sizes=ico_sizes)
        print("✅ ICO created: favicon.ico (multi-size)")
        
        print("\n✨ Favicon generation complete!")
        print("\nNext steps:")
        print("1. Update blog/templates/blog/base.html with favicon links")
        print("2. Add these lines to <head> section:")
        print('   <link rel="icon" type="image/png" href="{% static \'favicon.png\' %}" sizes="32x32">')
        print('   <link rel="icon" type="image/x-icon" href="{% static \'favicon.ico\' %}">')
        print('   <link rel="apple-touch-icon" href="{% static \'favicon.png\' %}">')
        print("3. Test in browser (clear cache first)")
        
        return True
        
    except ImportError as e:
        print(f"❌ Missing library: {e}")
        print("\nInstall required packages:")
        print("  pip install cairosvg pillow")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def generate_favicon_with_pillow_only():
    """Fallback: Simple color-based favicon using Pillow only"""
    try:
        from PIL import Image, ImageDraw
        
        project_root = Path(__file__).parent
        static_dir = project_root / "blog" / "static"
        static_dir.mkdir(parents=True, exist_ok=True)
        
        # Create 256x256 image with transparent background
        img = Image.new('RGBA', (256, 256), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        # Draw Link Chain Design
        # Left circle
        draw.ellipse([40, 93, 110, 163], outline=(37, 99, 235), width=18)
        # Right circle
        draw.ellipse([146, 93, 216, 163], outline=(37, 99, 235), width=18)
        # Connection bridge
        draw.rectangle([115, 118, 151, 138], fill=(37, 99, 235))
        
        png_file = static_dir / "favicon.png"
        img.save(png_file, 'PNG')
        print(f"✅ PNG favicon created: {png_file}")
        
        # Create multi-size ICO
        ico_sizes = [(256, 256), (128, 128), (64, 64), (48, 48), (32, 32), (16, 16)]
        ico_images = []
        for size in ico_sizes:
            ico_img = img.resize(size, Image.Resampling.LANCZOS)
            ico_images.append(ico_img)
        
        ico_file = static_dir / "favicon.ico"
        ico_images[0].save(ico_file, 'ICO', sizes=ico_sizes)
        print(f"✅ ICO favicon created: {ico_file}")
        
        print("\n✨ Favicon generation complete!")
        print("Note: For best quality, use the SVG conversion method with cairosvg")
        
        return True
        
    except ImportError as e:
        print(f"❌ Missing library: {e}")
        print("\nInstall Pillow:")
        print("  pip install pillow")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("🎯 LostLink Kenya Favicon Generator")
    print("=" * 60)
    print("\nAttempting to generate favicon...")
    
    # Try cairosvg first (better quality)
    if not generate_favicon_with_cairosvg():
        print("\n⚠️  cairosvg not available, using Pillow fallback...")
        if not generate_favicon_with_pillow_only():
            print("\n❌ Failed to generate favicon. Please install dependencies.")
            sys.exit(1)
    
    print("\n" + "=" * 60)
