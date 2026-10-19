# PDF documents — UI Tests

> **Implementation Order**: Tests are numbered for sequential TDD implementation.
> Start with the guest turned away, then the empty library, then a ready row, then what an upload does to that screen.

## 0. Prerequisite Guards

### 0.1 A guest who opens documents sees no list

Tier: 2 (hz-08)

```gherkin
Given a guest
When the guest opens documents
Then the guest sees the landing
And no document list is shown
And no upload door is shown
```

---

## 1. Page Display

### 1.1 An empty library shows the PDF door and no materials

Tier: 1 (hz-08)

```gherkin
Given a signed-in person with no documents
When the person opens documents
Then the heading is «Документы»
And the PDF door reads «Загрузить PDF» and «до 50 MB · парсинг и индексация»
And the presentation door reads «Создать презентацию»
And the list reads «Пока нет материалов»
```

### 1.2 A ready document shows its name, size, pages, and piece count

Tier: 1 (hz-01)

```gherkin
Given a signed-in person with a ready PDF named Матанализ.pdf
When the person opens documents
Then the row shows Матанализ.pdf
And the row shows the size, the page count, and the piece count
And the row shows «Готов»
And the row shows no failure reason
```

### 1.3 A list that is loading or that failed to load is not the empty library

Tier: 2 (hz-08)

```gherkin
Given a signed-in person opening documents
When the list is still loading
Then the screen does not read «Пока нет материалов»
When the list fails to load
Then the screen shows an error and a way to try again
And it does not spin forever
And it does not read «Пока нет материалов»
```

---

## 2. Upload on the screen

### 2.1 An accepted PDF appears as waiting and then becomes ready

Tier: 1 (hz-04)

```gherkin
Given a signed-in person with a ready document
When the person uploads a valid PDF
Then the new row appears at the top
And the new row shows «Ждёт»
And the earlier row is still there
And the new row later shows «В процессе» and then «Готов»
```

### 2.2 A refused upload names the reason and leaves the list

Tier: 2

```gherkin
Scenario Outline:
Given a signed-in person with a ready document
When the person <submits>
Then the screen shows <reason>
And the ready document is still the only row

Examples:
  | submits | reason |
  | submits a file that is not a PDF | the file is not a PDF |
  | submits a PDF over the maximum | the file is over 50 MB |
```

### 2.3 A failed document shows the failure and the reason

Tier: 2

```gherkin
Given a signed-in person with a document that failed on page 12
When the person opens documents
Then the row shows «Не удалось»
And the row shows that page 12 could not be read
```

### 2.4 A second press on one file adds one row

Tier: 2 (hz-02, hz-08)

```gherkin
Given a signed-in person on documents
When the person presses upload twice on one file before the first answer
Then one new row appears
```

### 2.5 An older status arriving late does not replace a newer one

Tier: 2 (hz-03, hz-08)

```gherkin
Given a document row that has already become «Готов»
When an older reply that says «В процессе» arrives
Then the row still shows «Готов»
```

### 2.6 Leaving before the upload is accepted leaves the list unchanged

Tier: 2 (hz-08)

```gherkin
Given a signed-in person who has chosen a PDF and has not been answered
When the person leaves documents
Then the list does not gain a row
And coming back shows the list from the server
```

---

## 6. Navigation

### 6.1 The presentation door does not upload a PDF

Tier: 2

```gherkin
Given a signed-in person on documents
When the person activates «Создать презентацию»
Then the document list is unchanged
And no PDF upload starts
```

---

## DSL Technical Reference

| DSL Statement | Technical Implementation |
|---------------|-------------------------|
| `opens documents` | The signed-in shell, Documents tab selected |
| `a guest` | No session. The landing is the only screen |
| `uploads a valid PDF` | The PDF door's file input, then the list reflects GET /api/v1/documents |
| `the screen shows the file is over 50 MB` | The refusal under the PDF door: «Файл больше 50 МБ. Список не изменился.» |
| `«Ждёт»` | status waiting |
| `«В процессе»` | status indexing |
| `«Готов»` | status ready |
| `«Не удалось»` | status failed |
