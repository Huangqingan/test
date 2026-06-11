"""
简单图片生成工具 — 基于 Pollinations.ai 免费 API
无需 API Key，无需注册，完全免费
"""
import urllib.request
import urllib.parse
import sys
import os

OUTPUT_DIR = os.path.dirname(os.path.abspath(__file__))


def generate_image(prompt: str, filename: str = "generated.png",
                   width: int = 1024, height: int = 768) -> str:
    """调用 Pollinations.ai 免费 API 生成图片"""
    encoded = urllib.parse.quote(prompt, safe="")
    url = f"https://image.pollinations.ai/prompt/{encoded}?width={width}&height={height}&nologo=true"

    print(f"Generating image...")
    print(f"   Prompt: {prompt[:80]}...")
    print(f"   Size: {width}x{height}")

    filepath = os.path.join(OUTPUT_DIR, filename)
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=120) as resp:
            data = resp.read()
        with open(filepath, "wb") as f:
            f.write(data)
        size_kb = os.path.getsize(filepath) / 1024
        print(f"Saved: {filepath} ({size_kb:.1f} KB)")
        return filepath
    except Exception as e:
        print(f"Failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    prompt = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else None
    if not prompt:
        prompt = input("请输入图片描述: ")
    generate_image(prompt)
