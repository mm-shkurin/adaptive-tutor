import { describe, expect, it } from 'vitest'
import { createRequestOrder } from './requestOrder'

describe('createRequestOrder', () => {
  it('keeps the newer save when an older answer arrives later', () => {
    const order = createRequestOrder()
    const older = order.start()
    const newer = order.start()
    expect(order.accepts(older)).toBe(false)
    expect(order.accepts(newer)).toBe(true)
  })
})
