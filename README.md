# 草原放松 · 抖音竖屏图

人躺在草原上放松的插画，9:16 竖屏（1080×1920），适合抖音 / 短视频封面或背景。

- `output/grassland_relax_1080x1920.png`：无损 PNG
- `output/grassland_relax_1080x1920.jpg`：体积更小的 JPG

## 重新生成

```bash
python3 src/scene.py out.html          # 生成 SVG 场景（HTML 包装）
node src/render.js out.html out.png    # 用 Playwright Chromium 渲染为 1080x1920 PNG
```

修改 `src/scene.py` 中的 `rng` 种子即可得到不同的草丛 / 花朵 / 云朵分布。
