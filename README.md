```
fly launch
fly secrets set BOT_API_TOKEN=
fly secrets set API_URL_REMBG=
fly deploy
fly scale count 1 --max-per-region 1
```