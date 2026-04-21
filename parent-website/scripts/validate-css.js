#!/usr/bin/env node
/**
 * CSS validation — catches the two bugs that broke articles page on prod:
 *   1. Unbalanced / nested braces  →  broken @media blocks
 *   2. Orphaned declarations       →  CSS props outside any selector
 *   3. Selector convention         →  .tabs without .tab base styles
 *
 * Run:  node scripts/validate-css.js
 * Auto: runs via "prebuild" before every `npm run build`
 */

const postcss = require('postcss')
const fs      = require('fs')
const path    = require('path')

const TARGET = path.resolve(__dirname, '../app')

// ── file discovery ────────────────────────────────────────────────────────────

function findCss(dir) {
  const out = []
  for (const e of fs.readdirSync(dir, { withFileTypes: true })) {
    const full = path.join(dir, e.name)
    if (e.isDirectory() && e.name !== 'node_modules') out.push(...findCss(full))
    else if (e.isFile() && e.name.endsWith('.css'))   out.push(full)
  }
  return out
}

// ── check 1: postcss parse (hard syntax errors) ───────────────────────────────

function checkParse(src) {
  try { postcss.parse(src); return null }
  catch (e) { return `syntax error: ${e.message}` }
}

// ── check 2: orphaned declarations (props outside any selector) ───────────────
// Tracks brace depth line-by-line; flags `prop: value;` at depth 0.

function checkOrphans(src) {
  const lines    = src.split('\n')
  const orphans  = []
  let depth      = 0
  let inComment  = false

  for (let li = 0; li < lines.length; li++) {
    const line = lines[li]
    let inStr = false, strCh = ''

    for (let i = 0; i < line.length; i++) {
      const c = line[i], n = line[i + 1]
      if (inComment) { if (c === '*' && n === '/') { inComment = false; i++ }; continue }
      if (inStr)     { if (c === strCh) inStr = false; continue }
      if (c === '/' && n === '*') { inComment = true; i++; continue }
      if (c === '"' || c === "'") { inStr = true; strCh = c; continue }
      if (c === '{') depth++
      else if (c === '}') depth--
    }

    if (depth === 0 && !inComment) {
      const t = line.trim()
      // property: value; at depth 0 → orphaned
      if (/^[\w-]+\s*:/.test(t) && t.includes(';') && !t.startsWith('//')) {
        orphans.push(`line ${li + 1}: "${t}"`)
      }
    }
  }

  return orphans.length
    ? `orphaned declarations (outside any selector):\n${orphans.map(o => '    ' + o).join('\n')}`
    : null
}

// ── check 3: selector naming convention ──────────────────────────────────────
// If a "container" class has styles, its "item" class must also have base styles.
// Example: .tabs → .tab, .cards → .card

const PAIRS = [
  ['.tabs',    '.tab'   ],
  ['.cards',   '.card'  ],
  ['.buttons', '.button'],
  ['.tags',    '.tag'   ],
]

function checkConventions(src) {
  let root
  try { root = postcss.parse(src) } catch { return null }

  const withDecls = new Set()
  root.walkRules(rule => {
    if ([...rule.nodes].some(n => n.type === 'decl')) {
      rule.selector.split(',').forEach(sel => {
        // strip leading ID scopes like #article-page-root
        withDecls.add(sel.trim().replace(/^#[\w-]+\s+/, ''))
      })
    }
  })

  const violations = []
  for (const [container, item] of PAIRS) {
    const hasContainer = [...withDecls].some(s => s === container || s.endsWith(' ' + container))
    const hasItem      = [...withDecls].some(s => s === item      || s.endsWith(' ' + item))
    if (hasContainer && !hasItem) {
      violations.push(
        `"${container}" has styles but "${item}" has no base styles` +
        ` — child elements will fall back to browser defaults`
      )
    }
  }
  return violations.length ? violations.join('\n  ') : null
}

// ── runner ────────────────────────────────────────────────────────────────────

const files  = findCss(TARGET)
let   failed = false

for (const file of files) {
  const src    = fs.readFileSync(file, 'utf8')
  const rel    = path.relative(path.resolve(__dirname, '..'), file)
  const errors = [checkParse(src), checkOrphans(src), checkConventions(src)].filter(Boolean)

  if (errors.length > 0) {
    failed = true
    console.error(`\n❌  ${rel}`)
    errors.forEach(e => console.error(`     ${e}`))
  } else {
    console.log(`✅  ${rel}`)
  }
}

if (failed) {
  console.error('\nCSS validation failed — fix errors above before committing.\n')
  process.exit(1)
} else {
  console.log('\nAll CSS files passed.\n')
}
