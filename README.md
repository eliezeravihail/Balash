# בלש

ארגז כלים לפיקוח מבוסס AI. בלוקי תוכנה דטרמיניסטיים ובלוקי הרנס שאורזים את המודל למטרה אחת עם מפרט קלט ופלט מדויק, משורשרים בקונפיגורציה לצינורות.

- **תכנון:** [docs/balash-design.md](docs/balash-design.md)
- **המוצר הראשון, מעקב קניות אישי מוואטסאפ:** [docs/personal-groceries.md](docs/personal-groceries.md)
- **מחקר שוק:** התיקייה `reports`

## התחלה מהירה

```bash
pip install -e ".[dev]"
python -m pytest            # רץ בלי מפתח API
balash init
export ANTHROPIC_API_KEY=...
balash ingest receipt.jpg
```

## מבנה

```
balash/
  core/            רשומה, בלוק, צינור, אחסון, עזרי טקסט
  harness/         סביבת ההרנס: טעינת מפרט, קריאה למודל, אימות, מטמון, ניסיון חוזר
  harness_blocks/  בלוק הרנס = תיקייה: block.yaml, prompt.md, schema.json
  blocks/          בלוקי התוכנה, ומחלקות הדבק של בלוקי ההרנס
  channels/        וואטסאפ ומסוף
  app.py           שרת ה-webhook והמתזמן החודשי
  cli.py           שורת פקודה
config/
  pipelines/       הצינורות, קובץ YAML לכל אחד
  instance.example.yaml
tests/
```
