const EMPTY_LIST = 'Пока нет материалов'

export function libraryView(page) {
  const emptyList = page.documents.length === 0 ? EMPTY_LIST : null
  return {
    heading: 'Документы',
    pdfDoor: {
      title: 'Загрузить PDF',
      hint: 'до 50 MB · парсинг и индексация',
    },
    presentationDoor: 'Создать презентацию',
    emptyList,
  }
}
