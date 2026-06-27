---
name: storyboard-image-generator
description: Use when Codex needs to generate storyboard sheet images, shot reference images, or visual frames from ad storyboard prompts through the Apifox-documented image generation API, especially for vertical 9:16 TikTok/UGC storyboard production.
---

# Storyboard Image Generator

Generate storyboard images through the configured image API instead of browser automation or built-in image tools.

## Environment

Require these environment variables before calling the script:

```bash
export STORYBOARD_IMAGE_BASE_URL="https://your-api-host"
export STORYBOARD_IMAGE_API_KEY="..."
export STORYBOARD_IMAGE_MODEL="auto-image"
```

Optional:

```bash
export STORYBOARD_IMAGE_SIZE="1024x1536"
export STORYBOARD_IMAGE_OUTPUT_DIR="downloads/storyboard-images"
```

## Workflow

1. Write a production-ready prompt for a storyboard sheet or a single storyboard frame.
2. Run `scripts/storyboard_image_tool.py submit` with `--wait --download` for normal use.
3. Use `query` when a task id already exists.
4. Use `download` when a task is complete and the content endpoint should be saved locally.

## Commands

Text-to-image storyboard sheet:

```bash
python3 skills/storyboard-image-generator/scripts/storyboard_image_tool.py submit \
  --prompt-file prompt.txt \
  --size 1024x1536 \
  --wait \
  --download
```

Image/reference-guided generation:

```bash
python3 skills/storyboard-image-generator/scripts/storyboard_image_tool.py submit \
  --prompt "保持参考图主体不变，生成 15 秒竖屏分镜图表" \
  --image "https://example.com/reference.png" \
  --wait \
  --download
```

Query or download:

```bash
python3 skills/storyboard-image-generator/scripts/storyboard_image_tool.py query --task-id TASK_ID
python3 skills/storyboard-image-generator/scripts/storyboard_image_tool.py download --task-id TASK_ID
```

## Prompt Rules

For storyboard sheets, use the old production storyboard table style: dense but readable cells, 6 rows, thumbnail reference frames, shot notes, camera notes, TTS/audio, and duration.

```text
Create a professional production storyboard sheet for a 15-second vertical 9:16 Mexican TikTok Shop UGC ad.
Format: clean table, 6 rows, columns: Shot No., Scene / Action Design, Reference Frame, Shot Size / Composition, Camera Movement, Camera Settings / Lighting, TTS / Subtitles / SFX, Duration.
Storyboard thumbnails must show only raw camera scenes. Do not add TikTok UI, watermarks, shopping cart stickers, subtitles, or text overlays inside the thumbnails.
Style: realistic cinematic storyboard thumbnails, phone-shot UGC energy, readable English table text.
Language rule: all text in the storyboard sheet must be English except TTS/dialogue lines, which may be Mexican Spanish.
Conflict hook rule: frame 01 must show a bold visual contrast like role reversal, luxury-vs-basic mismatch, exaggerated household battle, staged disaster, or social embarrassment. The conflict must be visually obvious without reading captions.
Quality rule: explicitly ask for 4K clarity, crisp frame thumbnails, sharp product details, and readable table text. Keep API `size` at the normal default unless the user asks otherwise.
Shots:
1. ...
```

Keep brand logos out unless the user supplies a brand. Keep the frame prompt visual and concrete: location, subject, action, camera distance, lighting, and props.

## API Reference

For endpoint details and payload shape, read `references/api.md`.
