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
}
