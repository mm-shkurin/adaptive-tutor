export function moveSlide(slides, slideId, direction) {
  const index = slides.findIndex((slide) => slide.id === slideId)
  if (index < 0) return null
  const target = direction === 'up' ? index - 1 : index + 1
  if (target < 0 || target >= slides.length) return null
  const next = slides.slice()
  const [item] = next.splice(index, 1)
  next.splice(target, 0, item)
  return next.map((slide) => slide.id)
}
