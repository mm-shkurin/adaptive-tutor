export function canDeleteAccount(typed, email) {
  return email !== '' && typed === email
}
