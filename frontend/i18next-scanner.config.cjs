const path = require('path')
const fs = require('fs')

const lngs = ['en', 'uk']

module.exports = {
  input: [
    'src/**/*.{js,jsx,ts,tsx}',
    // Ігноруємо самі файли перекладів, щоб сканер не намагався їх парсити
    '!src/shared/lib/i18n/translations/**',
  ],
  output: './',
  options: {
    debug: false,
    removeUnusedKeys: true,
    sort: true,
    ns: ['translations'],
    defaultNs: 'translations',
    keySeparator: false,
    nsSeparator: false,
    func: {
      list: ['t'],
      extensions: ['.js', '.jsx', '.ts', '.tsx'],
    },
    lngs,
    // Видаляємо секцію resource звідси, щоб бібліотека не намагалася
    // автоматично читати/писати .ts файли як JSON
    resource: {
      loadPath: '',
      savePath: '',
    },
  },
  transform(file, _enc, done) {
    const parser = this.parser
    const content = (file && file.contents && file.contents.toString('utf8')) || ''

    const re = /(?:^|[^\w$])t\s*\(\s*(['"`])((?:\\.|(?!\1).)*)\1/gm
    let match
    while ((match = re.exec(content)) !== null) {
      const key = match[2].trim()
      if (key) {
        parser.set(key, key, { ns: 'translations' })
      }
    }
    done()
  },
  flush(done) {
    const savePathPattern = 'src/shared/lib/i18n/translations/{{lng}}.ts'

    lngs.forEach(lng => {
      const filePath = path.join(process.cwd(), savePathPattern.replace('{{lng}}', lng))
      let existingData = {}

      // 1. Читаємо існуючі переклади вручну
      if (fs.existsSync(filePath)) {
        try {
          const fileContent = fs.readFileSync(filePath, 'utf8')
          const match = fileContent.match(/export const \w+ = (\{[\s\S]*\});?/)
          if (match && match[1]) {
            // Використовуємо Function для безпечного перетворення JS-об'єкта в дані
            existingData = new Function(`return ${match[1]}`)()
          }
        } catch (e) {
          console.error(`Could not parse ${lng}.ts:`, e.message)
        }
      }

      // 2. Отримуємо нові ключі, знайдені сканером
      const res = (this.resStore && this.resStore[lng]) || {}
      const newData = res.translations || {}

      // 3. Зливаємо дані (старі переклади мають пріоритет)
      const finalData = { ...newData, ...existingData }

      // 4. Сортуємо
      const sortedData = {}
      Object.keys(finalData).sort().forEach(key => {
        sortedData[key] = finalData[key]
      })

      // 5. Записуємо назад у форматі TS
      const tsContent = `export const ${lng} = ${JSON.stringify(sortedData, null, 2)}\n`

      fs.mkdirSync(path.dirname(filePath), { recursive: true })
      fs.writeFileSync(filePath, tsContent, 'utf8')
    })

    done()
  },
}