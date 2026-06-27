# Image API Reference

Source documents:

- `https://xxp0w23uvv.apifox.cn/api-449690329` - submit image task, text only
- `https://xxp0w23uvv.apifox.cn/api-449690330` - submit image task, with reference image
- `https://xxp0w23uvv.apifox.cn/api-449690331` - query image task
- `https://xxp0w23uvv.apifox.cn/api-449690332` - download image content

## Endpoints

All paths are relative to `STORYBOARD_IMAGE_BASE_URL`.

Submit:

```http
POST /v1/images/generations?async=true
Authorization: Bearer <api_key>
Content-Type: application/json
```

Text payload:

```json
{
  "model": "auto-image",
  "prompt": "一只白色小狗坐在阳光充足的客厅里，写实摄影风格，细节清晰",
  "response_format": "url",
  "size": "1024x1024"
}
```

Reference image payload:

```json
{
  "model": "auto-image",
  "prompt": "保持参考图主体不变，改成高级杂志封面风格",
  "response_format": "url",
  "size": "1024x1024",
  "image": [
    "https://example.com/reference-1.png",
    "https://example.com/reference-2.png"
  ]
}
```

Query:

```http
GET /v1/images/{task_id}
Authorization: Bearer <api_key>
```

The Apifox note says to wait for `completed`, then read `data[0].url`.

Download:

```http
GET /v1/images/{task_id}/content
Authorization: Bearer <api_key>
```

Use this after completion to save the generated image bytes.
