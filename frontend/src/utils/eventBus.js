import mitt from 'mitt'

const eventBus = mitt()
export const EVENT_TYPES = {
  AVATAR_UPDATED: 'avatar_updated'
}

export default eventBus