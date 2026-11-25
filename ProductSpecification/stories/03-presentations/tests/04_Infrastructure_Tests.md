# Presentations — Infrastructure Tests

## 1. Fakes and wiring

### 1.1 The app starts when OCR and slide-LLM ports are configured as fakes in tests

Tier: 2 (hz-07)

```gherkin
Given the test application context
When the presentation index use case runs
Then OCR and chat-LLM ports are the test fakes
And no live Tesseract or freellmapi call is made
```

### 1.2 Missing virus configuration prevents accepting slide bytes

Tier: 2 (hz-07)

```gherkin
Given virus check is not configured
When the person adds an image slide
Then the add is refused
And no slide is stored
```
