import { QUESTION_COUNTS } from '../logic/createQuiz'
import { QuizBack } from './QuizBack'

export function CreateQuizForm({ screen }) {
  return (
    <>
      <QuizBack onClick={screen.backToList} disabled={screen.creating} />
      <div className="panel-head">
        <div>
          <h1>Новая викторина</h1>
          <p className="quiz-lead">Вопросы соберутся из выбранного PDF.</p>
        </div>
      </div>
      <form className="quiz-gen-form" data-testid="quiz-create" onSubmit={screen.generate}>
        {screen.formNotice ? (
          <p className="alert" role="alert" data-testid={screen.formNotice.id}>{screen.formNotice.text}</p>
        ) : null}
        <label htmlFor="quiz-doc">Документ</label>
        <select
          id="quiz-doc"
          data-testid="quiz-document"
          value={screen.selectedDocumentId}
          disabled={screen.creating || screen.pdfs.length === 0}
          onChange={(event) => screen.setDocumentId(event.target.value)}
        >
          {screen.pdfs.length === 0 ? <option value="">Нет готового PDF</option> : null}
          {screen.pdfs.map((pdf) => (
            <option key={pdf.id} value={pdf.id} data-testid="quiz-document-option">{pdf.name}</option>
          ))}
        </select>
        <label htmlFor="quiz-topic">Тема</label>
        <input
          id="quiz-topic"
          data-testid="quiz-topic"
          type="text"
          maxLength={200}
          placeholder="Например: собственные числа"
          value={screen.topic}
          disabled={screen.creating}
          onChange={(event) => screen.setTopic(event.target.value)}
        />
        <label htmlFor="quiz-count">Число вопросов</label>
        <select
          id="quiz-count"
          data-testid="quiz-count"
          value={screen.questionCount}
          disabled={screen.creating}
          onChange={(event) => screen.setQuestionCount(Number(event.target.value))}
        >
          {QUESTION_COUNTS.map((count) => (
            <option key={count} value={count}>{count}</option>
          ))}
        </select>
        {screen.createError ? (
          <p className="alert" role="alert" data-testid="quiz-create-error">{screen.createError}</p>
        ) : null}
        <div className="quiz-gen-actions">
          <button
            type="button"
            className="btn btn-outline"
            data-testid="quiz-cancel"
            disabled={screen.creating}
            onClick={screen.backToList}
          >
            Отмена
          </button>
          <button
            type="submit"
            className="btn btn-dark"
            data-testid="quiz-generate"
            disabled={screen.creating || screen.pdfs.length === 0 || screen.documentsFailed}
          >
            {screen.creating ? 'Собираем…' : 'Сгенерировать и начать'}
          </button>
        </div>
      </form>
    </>
  )
}
