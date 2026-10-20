export function createRequestOrder() {
  let current = 0
  return {
    start() {
      current += 1
      return current
    },
    accepts(requestId) {
      return requestId === current
    },
  }
}
