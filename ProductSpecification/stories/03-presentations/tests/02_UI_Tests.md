# Presentations — UI Tests

> **Implementation Order**: Door → editor empty draft → add from gallery → index feedback → list row → delete → progress screen. Camera is a file input with capture; no MediaStream assertion.

## 0. Prerequisite guards

### 0.1 A guest opening documents still sees the landing after auth wall

Tier: 1 (hz-08)

```gherkin
Given a guest
When the guest opens Documents
Then the landing is shown
And the presentation editor is not shown
```

---

## 1. Documents door and editor

### 1.1 Create presentation opens the editor

Tier: 1

```gherkin
Given a signed-in person on Documents
When the person activates «Создать презентацию»
Then the presentation editor is shown
And the title field is visible with maxlength 80
And the slide count reads 0
And no PDF upload starts
```

### 1.2 Gallery add shows a new slide card

Tier: 1

```gherkin
Given the presentation editor with an empty draft saved
When the person adds one jpeg from the gallery control
Then one slide card appears
And the slide count reads 1
```

### 1.3 Index with no slides stays on the editor with a refusal

Tier: 1 (hz-08)

```gherkin
Given the presentation editor with 0 slides
When the person activates «Готово · индексировать»
Then the editor remains open
And a no-slides refusal is shown
And status is not ready
```

### 1.4 After index the documents list shows a ready presentation row

Tier: 1

```gherkin
Given a draft with one slide that indexes successfully
When indexing finishes
Then Documents shows a presentation row with ready status
And the row name is the presentation title
```

---

## 2. Ready edit and delete

### 2.1 Ready editor shows text not photo

Tier: 2

```gherkin
Given a ready presentation opened in the editor
Then each slide shows recognized text
And no slide photo is shown
```

### 2.2 Delete removes the row from Documents

Tier: 1

```gherkin
Given a ready presentation on Documents
When the person deletes that presentation and confirms
Then the row is gone from Documents
```

---

## 3. Progress

### 3.1 Progress panel shows four stats and topic nodes

Tier: 1

```gherkin
Given a signed-in person with progress data
When the person opens Progress
Then average mastery, weak count, sessions this week, and quizzes finished are shown
And topic nodes are shown
And no edge lines are required for the test to pass
```

### 3.2 Weak list matches the weak count band

Tier: 2 (hz-01)

```gherkin
Given topics below and above 40%
When the person opens Progress
Then the weak list only includes topics below 40%
And the weak count equals that list length
```

### 3.3 Topic actions open quiz create and chat

Tier: 2

```gherkin
Given a topic detail on Progress
When the person activates «Викторина по теме»
Then quiz create for that topic and material is started
When the person activates «Спросить в чате»
Then chat for that material is shown
```
