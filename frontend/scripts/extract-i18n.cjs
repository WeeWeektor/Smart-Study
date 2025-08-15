const fs = require('fs')
const path = require('path')

const SRC_DIR = path.join(process.cwd(), 'src')
const OUT_DIR = path.join(process.cwd(), 'src/shared/lib/i18n/translations')

const FILE_EXTENSIONS = new Set(['.ts', '.tsx', '.js', '.jsx'])
const KEY_REGEX =
  /(?:^|[^\w$])(?:this\.)?t\s*\(\s*(['"`])((?:\\.|(?!\1).)*)\1/gm
const CLASS_TRANSLATOR_REGEX =
  /(?:^|[^\w$])ClassTranslator\.(?:t|translate)\s*\(\s*(['"`])((?:\\.|(?!\1).)*)\1/gm

function walk(dir) {
  const entries = fs.readdirSync(dir, { withFileTypes: true })
  const files = []
  for (const e of entries) {
    const full = path.join(dir, e.name)
    if (e.isDirectory()) {
      if (!full.includes(`${path.sep}translations${path.sep}`)) {
        files.push(...walk(full))
      }
    } else if (FILE_EXTENSIONS.has(path.extname(e.name))) {
      files.push(full)
    }
  }
  return files
}

function extractKeysFromFile(filePath) {
  const content = fs.readFileSync(filePath, 'utf8')
  const keys = new Set()

  let match
  while ((match = KEY_REGEX.exec(content)) !== null) {
    const key = match[2].trim()
    if (key) keys.add(key)
  }

  while ((match = CLASS_TRANSLATOR_REGEX.exec(content)) !== null) {
    const key = match[2].trim()
    if (key) keys.add(key)
  }

  return keys
}

function buildFlatTree(keys) {
  const tree = {}
  for (const k of keys) {
    tree[k] = k
  }
  return tree
}

function ensureDir(dir) {
  fs.mkdirSync(dir, { recursive: true })
}

function writeTs(lang, obj) {
  ensureDir(OUT_DIR)
  const outPath = path.join(OUT_DIR, `${lang}.ts`)
  const content = `export const ${lang} = ${JSON.stringify(obj, null, 2)}\n`
  fs.writeFileSync(outPath, content, 'utf8')
}

function main() {
  const files = walk(SRC_DIR)
  const allKeys = new Set()
  for (const f of files) {
    const keys = extractKeysFromFile(f)
    for (const k of keys) allKeys.add(k)
  }

  const tree = buildFlatTree(allKeys)
  writeTs('en', tree)
  writeTs('uk', tree)
  console.log(
    `Extracted ${allKeys.size} keys into translations/en.ts and uk.ts`
  )
}

main()
