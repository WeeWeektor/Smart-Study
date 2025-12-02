import { VideoFields } from '../ui/VideoFields'
import { AudioFields } from '../ui/AudioFields'
import { DocumentFields } from '../ui/DocumentFields'
import { PresentationFields } from '../ui/PresentationFields'
import { LinkFields } from '../ui/LinkFields'
import { ImageFields } from '../ui/ImageFields'
import { CodeFields } from '../ui/CodeFields'
import { TextFields } from '../ui/TextFields'

export const getLessonFields = (type: string) => {
  switch (type) {
    case 'video':
      return VideoFields

    case 'audio':
      return AudioFields

    case 'document':
      return DocumentFields

    case 'presentation':
      return PresentationFields

    case 'link':
      return LinkFields

    case 'live':
      return LinkFields

    case 'image':
      return ImageFields

    case 'code':
      return CodeFields

    case 'text':
      return TextFields

    case 'assignment':
      return TextFields

    default:
      return null
  }
}
