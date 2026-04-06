export const parseMarkdownToBlocks = (markdown: string) => {
  if (!markdown) return []
  const blocks: any[] = []

  const patterns = {
    title: /^#\s+(.+)$/,
    description: /^>\s+([\s\S]+?)$/,
    comment: /^\*\*\*Методичний коментар:\*\*\s*(.+?)\*$/,
    image: /!\[.*?\]\((.*?)\)/,
    video:
      /<video[\s\S]*?src="(.*?)"[\s\S]*?<\/video>(?:\s*\*\[🔗 .*?\]\((.*?)\)\*)?/,
    audio: /<audio[\s\S]*?src="(.*?)"[\s\S]*?<\/audio>/,
    code: /```(\w*)\n([\s\S]*?)```/,
    assignment: /^###\s+Завдання:\n([\s\S]+)$/,
    fileLink: /###\s+([🔗📊📄📝🔴])\s+\[(.*?)\]\((.*?)\)/u,
  }

  const segmentRegex =
    /(```[\s\S]*?```|<video[\s\S]*?<\/video>(?:\s*\*\[🔗 .*?\]\(.*?\)\*)?|<audio[\s\S]*?<\/audio>)/g
  const segments = markdown.split(segmentRegex)

  segments.forEach(segment => {
    if (!segment) return
    const trimmedSegment = segment.trim()
    if (
      !trimmedSegment ||
      (trimmedSegment.startsWith('http') && !trimmedSegment.includes('<video'))
    )
      return

    if (trimmedSegment.startsWith('```')) {
      const match = trimmedSegment.match(patterns.code)
      blocks.push({
        type: 'code',
        data: { language: match?.[1] || 'text', code: match?.[2].trim() || '' },
      })
    } else if (trimmedSegment.startsWith('<video')) {
      const match = trimmedSegment.match(patterns.video)
      const url = (match?.[1] || match?.[2] || '').replace(/\?$/, '')
      blocks.push({
        type: 'video',
        url: url,
        data: { previewUrl: url, fileKey: null },
      })
    } else if (trimmedSegment.startsWith('<audio')) {
      const match = trimmedSegment.match(patterns.audio)
      const url = (match?.[1] || '').replace(/\?$/, '')
      blocks.push({
        type: 'audio',
        url: url,
        data: { previewUrl: url },
      })
    } else {
      const lines = trimmedSegment.split(/\n\n+/)
      lines.forEach(line => {
        const trimmedLine = line.trim()
        if (!trimmedLine || trimmedLine.includes('🔗 Відкрити відео окремо'))
          return

        if (patterns.title.test(trimmedLine)) {
          blocks.push({ type: 'title', data: trimmedLine.replace(/^#\s+/, '') })
        } else if (patterns.description.test(trimmedLine)) {
          blocks.push({
            type: 'description',
            data: trimmedLine.replace(/^>\s+/, ''),
          })
        } else if (patterns.comment.test(trimmedLine)) {
          const match = trimmedLine.match(patterns.comment)
          blocks.push({ type: 'comment', data: match?.[1] })
        } else if (patterns.image.test(trimmedLine)) {
          const match = trimmedLine.match(patterns.image)
          const url = (match?.[1] || '').replace(/\?$/, '')
          blocks.push({
            type: 'image',
            url: url,
            data: { previewUrl: url, fileKey: null },
          })
        } else if (patterns.assignment.test(trimmedLine)) {
          const match = trimmedLine.match(patterns.assignment)
          blocks.push({ type: 'assignment', data: match?.[1].trim() })
        } else if (patterns.fileLink.test(trimmedLine)) {
          const match = trimmedLine.match(patterns.fileLink)
          const icon = match?.[1]
          const url = (match?.[3] || '').replace(/\?$/, '')
          const fileName = match?.[2] || ''

          let type = 'link'
          if (icon === '📊') type = 'presentation'
          if (icon === '📄' || icon === '📝') type = 'document'
          if (icon === '🔴') type = 'live'

          blocks.push({
            type,
            url: url,
            data:
              type === 'link' || type === 'live'
                ? url
                : { previewUrl: url, fileName: fileName, fileKey: null },
          })
        } else {
          blocks.push({ type: 'text', data: trimmedLine })
        }
      })
    }
  })

  return blocks
}
