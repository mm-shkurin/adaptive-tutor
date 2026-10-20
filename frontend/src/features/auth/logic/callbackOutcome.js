const MAX_OAUTH_CODE_LENGTH = 512

const REASONS = {
  state_invalid: 'Ссылка возврата устарела или пришла не с того устройства. Начните вход заново.',
  code_missing: 'Яндекс вернул нас без кода входа. Сессия не создана.',
  provider_failed: 'Яндекс не подтвердил вход. Сессия не создана.',
}

const DEFAULT_REASON = 'Яндекс не подтвердил вход. Сессия не создана.'

export const MALFORMED_CALLBACK = 'Адрес возврата неполный: кода входа в нём нет. Начните вход заново.'

export const EXCHANGE_REFUSED = 'Код входа не подошёл — возможно, он уже использован или истёк. Сессия не создана.'

export function callbackOutcome(params) {
  const error = params.get('error')
  if (error !== null) return { kind: 'refused', reason: REASONS[error] ?? DEFAULT_REASON }
  const code = params.get('code')?.trim() ?? ''
  if (!code || code.length > MAX_OAUTH_CODE_LENGTH) return { kind: 'malformed' }
  return { kind: 'exchange', code }
}
