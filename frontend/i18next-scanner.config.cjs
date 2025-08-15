const path = require('path')
const fs = require('fs')

const lngs = ['en', 'uk']
const resource = {
  loadPath: 'src/shared/lib/i18n/translations/{{lng}}.ts',
  savePath: 'src/shared/lib/i18n/translations/{{lng}}.ts',
}

module.exports = {
  input: ['src/**/*.{js,jsx,ts,tsx}', '!src/shared/lib/i18n/translations/**'],
  output: './',
  options: {
    debug: false,
    removeUnusedKeys: true,
    sort: true,
    ns: ['translations'],
    defaultNs: 'translations',
    keySeparator: '.',
    nsSeparator: ':',
    func: {
      list: ['t'],
      extensions: ['.js', '.jsx', '.ts', '.tsx'],
    },
    lngs,
    resource,
  },
  transform(file, _enc, done) {
    const parser = this.parser
    const content =
      (file && file.contents && file.contents.toString('utf8')) || ''

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
    lngs.forEach(lng => {
      const res = (this.resStore && this.resStore[lng]) || {}
      const data =
        res.translations ||
        (Object.keys(res).length ? res[Object.keys(res)[0]] : {})

      const filePath = path.join(
        process.cwd(),
        resource.savePath.replace('{{lng}}', lng)
      )

      const tsContent = `export const ${lng} = ${JSON.stringify(data, null, 2)}\n`

      fs.mkdirSync(path.dirname(filePath), { recursive: true })
      fs.writeFileSync(filePath, tsContent, 'utf8')
    })

    done()
  },
}
