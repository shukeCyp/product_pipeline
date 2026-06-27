---
name: mexico-ugc-storyboard
description: Create Mexico-market TikTok Shop / UGC ad storyboards and video-generation prompts. Use when Codex needs to design Spanish-for-Mexico product hooks, 15s vertical video shot plans, production storyboard tables, contrast-based visual concepts, or image/video prompts for Mexican ecommerce affiliate content.
---

# Mexico UGC Storyboard

Create execution-ready storyboards, not generic ad copy.

## Defaults

Unless the user explicitly says otherwise, always assume:

- Market: Mexico.
- Language: Mexican Spanish for dialogue, hooks, and voiceover.
- Format: 15-second vertical 9:16 TikTok Shop / UGC ad.
- Deliverable: production storyboard table first; image/video prompts only when requested.
- Tone: local Mexican UGC, not Spain Spanish, not neutral translated Spanish, not corporate ad copy.
- Product framing: generic product with no visible brand logo unless the user provides a brand.

## Output Shape

For storyboard requests, output a 15s vertical-video production table:

```text
镜号 | 画面内容 / 动作设计 | 画面参考 | 景别 / 构图 | 拍摄方式 | 拍摄参数 / 光影 | 台词 / 音效 | 时长
```

Do not put subtitles, TikTok Shop icons, carts, stickers, watermarks, or UI inside the storyboard frame prompt unless the user explicitly asks for final edited-video overlays.

## Creative Rules

- Start with visual conflict before product explanation.
- Use safe high-contrast setups: role reversal, status mismatch, absurd household behavior, social embarrassment, product-as-character, fake trial/funeral/breakup, luxury setting vs basic hygiene problem.
- Prefer bold executable hooks like the user's reference storyboard: an absurd character or status mismatch doing a mundane product task, e.g. a muscular man in a maid outfit fighting a filthy pan, an elegant person selling a cheap household product on a luxury car hood, a person in protective gear battling bathroom stains, a party scene treated like a disaster scene, or an expensive-looking setup ruined by a basic home problem.
- The conflict should be visual and immediate, not just ad copy. It must be understandable from frame 01 without reading captions.
- Avoid racial conflict, protected-class mockery, sexualized framing, and humiliation of real people.
- Spanish must sound Mexican, not translated: prefer `güey`, `la neta`, `sí jaló`, `chafa`, `huele a humedad`, `huele a guardado`, `no manches` when appropriate.
- Keep product proof simple: problem, wrong approach, product rescue, visible result, light CTA.
- For generated storyboard images, ask for raw camera scenes in each thumbnail, not final TikTok overlays.

## 15s Structure

```text
0-2s   visual hook / absurd conflict
2-6s   wrong method fails
6-9s   product rescue
9-12s  fast proof
12-15s CTA / payoff
```

## Storyboard Image Prompt Pattern

Use this when generating a storyboard sheet image:

```text
Create a professional production storyboard sheet for a 15-second vertical 9:16 Mexican TikTok Shop UGC ad.
Format: clean table, 6 rows, columns: Shot No., Scene / Action Design, Reference Frame, Shot Size / Composition, Camera Movement, Camera Settings / Lighting, TTS / Subtitles / SFX, Duration.
Important: storyboard frame thumbnails must show only raw camera scenes. Do not add subtitles, TikTok Shop icons, shopping cart stickers, UI, watermarks, or text overlays inside the frame thumbnails.
Style: realistic cinematic storyboard thumbnails, phone-shot UGC energy, Mexican home setting, readable English table text.
Language rule: all table labels and production notes must be English; only TTS/dialogue lines may be Mexican Spanish.
[Insert six shot descriptions.]
```

## Video Prompt Pattern

Use this when creating a video-generation prompt:

```text
Create a 15-second vertical 9:16 UGC-style video ad for the Mexican market.
Product: [generic product], no visible brand logo.
Style: handheld phone video, natural Mexican home setting, funny chaotic UGC, not polished commercial.
No subtitles, TikTok Shop icons, UI elements, watermarks, stickers, or text overlays unless requested.
Shots:
1. 0-2s: [visual hook]
2. 2-4s: [wrong method / escalation]
3. 4-6s: [failure / social reaction]
4. 6-9s: [product enters]
5. 9-12s: [proof montage]
6. 12-15s: [payoff / CTA]
Voiceover in Mexican Spanish:
[lines]
Avoid: real logos, racial jokes, protected-class conflict, sexualized framing, polished studio ad look.
```

## Example: Laundry Detergent

Concept: muscular bearded man in cute maid apron and pink rubber gloves tries to defeat smelly laundry by force; detergent solves it.

Key lines:

```text
Yo contra la ropa apestosa.
Le puse fuerza...
Güey... todavía huele raro.
No es fuerza. Es detergente.
No manches... sí jaló.
Si tu ropa huele a humedad, prueba este.
```
