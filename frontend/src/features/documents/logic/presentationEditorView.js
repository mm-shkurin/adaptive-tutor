export function slideCountLabel(count) {
  const value = Math.abs(count) % 100
  const last = value % 10
  if (value > 10 && value < 20) return `${count} слайдов`
  if (last === 1) return `${count} слайд`
  if (last >= 2 && last <= 4) return `${count} слайда`
  return `${count} слайдов`
}