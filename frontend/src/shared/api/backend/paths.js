const V1 = '/api/v1'

export const BACKEND = {
  auth: {
    yandexStart: `${V1}/auth/oauth/yandex/start`,
    oauthExchange: `${V1}/auth/oauth/exchange`,
    refresh: `${V1}/auth/refresh`,
    logout: `${V1}/auth/logout`,
  },
  user: {
    profile: `${V1}/user/profile`,
    avatar: `${V1}/user/avatar`,
    account: `${V1}/user`,
  },
  documents: {
    list: `${V1}/documents`,
    item: (id) => `${V1}/documents/${id}`,
    statusEvents: `${V1}/documents/status-events`,
  },
  chats: {
    list: `${V1}/chats`,
    open: `${V1}/chats/open`,
    item: (id) => `${V1}/chats/${id}`,
    messages: (id) => `${V1}/chats/${id}/messages`,
  },
  quizzes: {
    list: `${V1}/quizzes`,
    item: (id) => `${V1}/quizzes/${id}`,
    answers: (id) => `${V1}/quizzes/${id}/answers`,
    advance: (id) => `${V1}/quizzes/${id}/advance`,
    retries: (id) => `${V1}/quizzes/${id}/retries`,
  },
  presentations: {
    create: `${V1}/presentations`,
    item: (id) => `${V1}/presentations/${id}`,
    slides: (id) => `${V1}/presentations/${id}/slides`,
    index: (id) => `${V1}/presentations/${id}/index`,
  },
  progress: `${V1}/progress`,
}
