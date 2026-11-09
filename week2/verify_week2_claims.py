"""
Week 2 notes -- claim checker.

Every check takes one statement (or code snippet) from the week2 notes and runs
it for real:

    * text encodings / number systems ........ Python (exact arithmetic, codecs)
    * HTML & CSS behaviour ................... headless Chromium (playwright): computed styles,
                                               layout boxes, selector matching, the cascade
    * HTML validity .......................... the official Nu HTML validator (vnu.jar) on every
                                               ```html snippet and on the obsolete-attribute claims
    * CSS syntax ............................. CSS.supports() on every declaration / selector in
                                               every ```css snippet
    * Bootstrap <link integrity="..."> ....... sha384 of the real bootstrap.min.css

and reports whether the notes are right:

    OK     -> the notes say what actually happens
    WRONG  -> the notes say something that does not happen (the evidence shows what does)

A check usually has two halves: the FACT (measured here) and the NOTE TEXT (the
markdown contains the correct statement and not the wrong one). The claims are
written as the notes state them *after* the accuracy fixes, so a clean run ends
with "0 WRONG".

Run (from anywhere):
    python week2/verify_week2_claims.py

Optional tools (a check that needs a missing tool is skipped and listed at the end):
    node + playwright (global)             -> all browser checks (pre-installed in Claude Code cloud)
    VNU_JAR=/path/to/vnu.jar  + java       -> HTML validation        (npm install vnu-jar)
    BOOTSTRAP_CSS=/path/bootstrap.min.css  -> Bootstrap SRI hash     (npm install bootstrap@5.3.5)

Checked against CPython 3.13, Chromium (playwright 1.63), Nu validator 24.x.
"""
import base64
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from fractions import Fraction
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
VERBOSE = "-v" in sys.argv
RESULTS, SKIPPED = [], []


# --------------------------------------------------------------------------- #
# helpers
# --------------------------------------------------------------------------- #
def note(name):
    return (HERE / name).read_text(encoding="utf-8")


def check(file, claim, fn):
    """fn() returns (notes_are_correct: bool, evidence: str)."""
    try:
        ok, evidence = fn()
    except Exception as e:
        ok, evidence = False, f"raised {type(e).__name__}: {str(e).splitlines()[0][:150]}"
    RESULTS.append((ok, file))
    print(f"[{'OK   ' if ok else 'WRONG'}] {file}\n        claim   : {claim}\n        actual  : {evidence}\n")


def has(text, pattern, flags=re.I | re.S):
    return re.search(pattern, text, flags) is not None


def md_files():
    return sorted(HERE.glob("*.md"))


def blocks(text, langs):
    """[(line_no, body)] of fenced blocks whose info-string starts with one of langs."""
    out = []
    for m in re.finditer(r"^[ \t]*```[ \t]*(\w*)[^\n]*\n(.*?)^[ \t]*```", text, re.S | re.M):
        if m.group(1).lower() in langs:
            out.append((text[: m.start()].count("\n") + 2, m.group(2)))
    return out


def github_slug(heading):
    s = re.sub(r"[`*_]", "", heading.strip().lower())
    return re.sub(r"[^\w\- ]", "", s, flags=re.UNICODE).replace(" ", "-")


def strip_fences(text):
    return re.sub(r"^[ \t]*```.*?^[ \t]*```", "", text, flags=re.S | re.M)


# --------------------------------------------------------------------------- #
# 2-1-ascii-unicode.md
# --------------------------------------------------------------------------- #
def ascii_facts():
    ranges = ((ord("0"), ord("9")) == (48, 57) and (ord("A"), ord("Z")) == (65, 90) and (ord("a"), ord("z")) == (97, 122))
    a, la = format(ord("A"), "08b"), format(ord("a"), "08b")
    bit5 = all((ord(c.lower()) ^ ord(c.upper())) == 0x20 and not ord(c.upper()) & 0x20 and ord(c.lower()) & 0x20 for c in "AbZq")
    punct_in_ascii = all(ord(c) < 128 for c in "!@#%&*()-/")
    try:
        "Ľ".encode("latin-1")
        lcaron = True
    except UnicodeEncodeError:
        lcaron = False
    latin1_ok = all(len(c.encode("latin-1")) == 1 for c in "éüñ£©")
    t = note("2-1-ascii-unicode.md")
    bad = has(t, r"include `!@# %&\*\(\) -Ľätīń/Rõman` symbols")
    good = has(t, r"(é|é).{0,40}(ü|ü)") and has(t, r"already (in|part of) ASCII|are (already )?ASCII")
    return (ranges and a == "01000001" and la == "01100001" and bit5 and punct_in_ascii and not lcaron and latin1_ok and 2**7 == 128
            and not bad and good), (
        f"digits 48-57, A-Z 65-90, a-z 97-122; 'A'={a}, 'a'={la}; case differs only in bit 5 (0x20): {bit5}; '!@#%&*()-/' are plain ASCII: {punct_in_ascii}; "
        f"'Ľ' does NOT fit Latin-1 ({not lcaron}) while 'é ü ñ £ ©' do ({latin1_ok}); note no longer lists plain-ASCII symbols as 'extended': {not bad}; gives real extended examples: {good}")


def unicode_facts():
    cps = (ord("a") == 0x61 and ord("अ") == 0x905 and ord("😀") == 0x1F600)
    space = 0x10FFFF + 1
    t = note("2-1-ascii-unicode.md")
    good = has(t, r"1,114,112") and has(t, r"U\+10FFFF")
    return cps and space == 1_114_112 and 2**16 == 65_536 and 2**32 == 4_294_967_296 and good, (
        f"'a'=U+0061, 'अ'=U+0905, 😀=U+1F600; Unicode defines {space:,} code points (0..U+10FFFF) although 32 bits could hold {2**32:,}; note says so: {good}")


def problem_one():
    chars = 5000
    vals = (32 * chars, 8 * chars, 7 * chars, 6 * chars)
    t = note("2-1-ascii-unicode.md")
    good = all(has(t, re.escape(s)) for s in ("160{,}000", "40{,}000", "35{,}000", "30{,}000"))
    bad = has(t, r"wastes `?32 bits")
    return vals == (160_000, 40_000, 35_000, 30_000) and good and not bad, (
        f"{vals} bits; note says 'A' wastes 32 bits: {bad} (it takes 32 bits of which 7 are needed, i.e. 25 are wasted)")


def utf8_table():
    edges = {0x7F: 1, 0x80: 2, 0x7FF: 2, 0x800: 3, 0xFFFF: 3, 0x10000: 4, 0x10FFFF: 4}
    lens = {cp: len(chr(cp).encode("utf-8")) for cp in edges}
    prefixes = {1: "0", 2: "110", 3: "1110", 4: "11110"}
    pref_ok = all(format(chr(cp).encode("utf-8")[0], "08b").startswith(prefixes[n]) for cp, n in edges.items()) and \
        all(format(b, "08b").startswith("10") for cp in (0x7FF, 0xFFFF, 0x10FFFF) for b in chr(cp).encode("utf-8")[1:])
    decimals = (0x7F, 0x7FF, 0xFFFF, 0x10FFFF) == (127, 2047, 65535, 1114111)
    try:
        "\ud800".encode("utf-8")
        surrogate_ok = True
    except UnicodeEncodeError:
        surrogate_ok = False
    u16 = (len("A".encode("utf-16-be")), len("😀".encode("utf-16-be")))
    u32 = {len(c.encode("utf-32-be")) for c in "A😀"}
    t = note("2-1-ascii-unicode.md")
    good = has(t, r"U\+D800.{0,10}U\+DFFF") and has(t, r"surrogate") and not has(t, r"does NOT use prefix bits")
    return lens == edges and pref_ok and decimals and not surrogate_ok and u16 == (2, 4) and u32 == {4} and good, (
        f"UTF-8 length at each boundary: {lens}; lead-byte prefixes 0/110/1110/11110 and 10xxxxxx continuation bytes confirmed; "
        f"U+D800..U+DFFF (surrogates) cannot be encoded: {not surrogate_ok}; UTF-16: 'A'={u16[0]} bytes, 😀={u16[1]} bytes; UTF-32 always {u32}; "
        f"note mentions the surrogate gap and surrogate pairs (not 'no prefix bits'): {good}")


# --------------------------------------------------------------------------- #
# 2-2-number-systems.md
# --------------------------------------------------------------------------- #
def number_systems():
    f = lambda s, b: int(s, b)
    worked = (f("11001", 2) == 25 and f("623", 8) == 403 and f("1C7", 16) == 455 and f("0110", 2) == 6 and 384 == 3 * 100 + 8 * 10 + 4
              and format(f("11011010", 2), "X") == "DA" and format(254, "X") == "FE" and format(f("10111101", 2), "o") == "275"
              and f("572", 8) == 378 and f("9B", 16) == 155 and 254 // 16 == 15 and 254 % 16 == 14)
    exercises = (f("110101", 2) == 53 and format(45, "b") == "101101" and format(f("11101101", 2), "X") == "ED"
                 and f("624", 8) == 404 and format(f("3F", 16), "b") == "111111")
    fraction = Fraction(5, 8) == Fraction(1, 2) + Fraction(0, 4) + Fraction(1, 8)       # 0.625 = 0.101_2
    n_bits = all(2**n - 1 == int("1" * n, 2) for n in range(1, 17))
    py = (bin(45) == "0b101101" and oct(254) == "0o376" and hex(254) == "0xfe" and int("101101", 2) == 45 and int("376", 8) == 254 and int("FE", 16) == 254)
    t = note("2-2-number-systems.md")
    bad_arith = has(t, r"5 \\times 16 \+ 7 \\times 8")      # 8^2 is 64, not 16
    good_arith = has(t, r"5 \\times 64 \+ 7 \\times 8 \+ 2 \\times 1")
    answers = all(has(t, p) for p in (r"(?<!\d)53(?!\d)", r"101101", r"ED_", r"(?<!\d)404(?!\d)", r"111111"))
    return worked and exercises and fraction and n_bits and py and not bad_arith and good_arith and answers, (
        f"all 10 worked conversions correct: {worked}; exercise answers 53, 101101, ED, 404, 111111: {exercises}; 0.625 = 0.101 in binary: {fraction}; "
        f"octal example wrote '5 x 16' for 5 x 8^2 (8^2 = 64, the next line 320 was right): old text present {bad_arith}, fixed text present {good_arith}; "
        f"note now gives the exercise answers: {answers}; the Python one-liners in the note (bin(45), oct(254), hex(254), int(..., base)) are right: {py}")


# --------------------------------------------------------------------------- #
# headless Chromium: one node process runs every browser check
# --------------------------------------------------------------------------- #
BROWSER_JS = r"""
const { chromium } = require('playwright');
const fs = require('fs');
(async () => {
  const input = JSON.parse(fs.readFileSync(process.argv[2], 'utf8'));
  const b = await chromium.launch();
  const ctx = await b.newContext({ viewport: { width: 1000, height: 800 } });
  const page = await ctx.newPage();
  const R = {};
  const doc = (body, head = '') => `<!DOCTYPE html><html lang="en"><head><meta charset="utf-8">${head}</head><body style="margin:0">${body}</body></html>`;
  const run = async (name, html, fn, arg) => { await page.setContent(html); R[name] = await page.evaluate(fn, arg); };
  const color = (name, html) => run(name, html, () => getComputedStyle(document.querySelector('#t')).color);

  // --- doctype / parsing
  await page.setContent('<!DOCTYPE html><p>x'); R.compat_doctype = await page.evaluate(() => document.compatMode);
  await page.setContent('<p>x');                R.compat_none    = await page.evaluate(() => document.compatMode);
  await run('div_selfclose', doc('<div/><p>x</p>'), () => !!document.querySelector('div > p'));
  await run('implicit_tbody', doc('<table><tr id=r1><td>1</td></tr><tr id=r2><td>2</td></tr><tr id=r3><td>3</td></tr></table>'),
    () => ({ first: document.querySelector('table').firstElementChild.tagName, odd: [...document.querySelectorAll('table tr:nth-child(odd)')].map(e => e.id),
             direct: document.querySelectorAll('table > tr').length }));

  // --- default display, inline vs replaced elements
  await run('display', doc('<div></div><p></p><h1></h1><form></form><section></section><ul><li></li></ul><span></span><a href=#></a><img alt=""><strong></strong><em></em><input><table></table>'),
    () => Object.fromEntries(['div','p','h1','form','section','ul','li','span','a','img','strong','em','input','table'].map(t => [t, getComputedStyle(document.querySelector(t)).display])));
  await run('inline_width', doc('<span id=s style="width:300px;height:80px;background:red">hi</span><br><img id=i width=300 height=200 alt="" src="data:image/gif;base64,R0lGODlhAQABAAAAACw=">' +
    '<br><span id=ib style="display:inline-block;width:100px;height:50px">x</span>'),
    () => { const r = id => document.getElementById(id).getBoundingClientRect(); return { span: [r('s').width, r('s').height], img: [r('i').width, r('i').height], inlineBlock: [r('ib').width, r('ib').height] }; });
  await run('block_width', doc('<div style="width:800px"><div id=d>a</div><p id=p>b</p><span id=s>c</span></div>'),
    () => { const w = id => document.getElementById(id).getBoundingClientRect().width; return { div: w('d'), p: w('p'), span: w('s') }; });
  await run('th_defaults', doc('<table><tr><th id=h>H</th><td id=d>D</td></tr></table>'),
    () => ({ thWeight: getComputedStyle(h).fontWeight, thAlign: getComputedStyle(h).textAlign, tdWeight: getComputedStyle(d).fontWeight, collapse: getComputedStyle(document.querySelector('table')).borderCollapse }));
  await run('boxsizing', doc('<div id=x></div>'), () => getComputedStyle(x).boxSizing);

  // --- the cascade (specificity, order, !important, origin of the rule)
  await color('case1_later', doc('<style>.a{color:rgb(255,0,0)}.b{color:rgb(0,0,255)}</style><p id=t class="a b">x</p>'));
  await color('case1_swapped', doc('<style>.b{color:rgb(0,0,255)}.a{color:rgb(255,0,0)}</style><p id=t class="a b">x</p>'));
  await color('case2_id_vs_class', doc('<style>#t{color:rgb(255,0,0)}.c{color:rgb(0,0,255)}</style><p id=t class=c>x</p>'));
  await color('case3_inline', doc('<style>#t{color:rgb(255,0,0)}</style><p id=t style="color:rgb(0,0,255)">x</p>'));
  await color('case4_important', doc('<style>.c{color:rgb(0,0,255) !important}#t{color:rgb(255,0,0)}</style><p id=t class=c style="color:rgb(0,128,0)">x</p>'));
  await color('case5_id_important', doc('<style>.c{color:rgb(0,0,255) !important}#t{color:rgb(255,0,0) !important}</style><p id=t class=c>x</p>'));
  await color('case5_equal_later', doc('<style>.a{color:rgb(0,0,255) !important}.b{color:rgb(255,0,0) !important}</style><p id=t class="a b">x</p>'));
  await color('case5_inline_important', doc('<style>#t{color:rgb(255,0,0) !important}</style><p id=t style="color:rgb(0,0,255) !important">x</p>'));
  const many = Array.from({ length: 30 }, (_, i) => 'c' + i);
  await color('many_classes_vs_id', doc(`<style>#t{color:rgb(255,0,0)}.${many.join('.')}{color:rgb(0,0,255)}</style><p id=t class="${many.join(' ')}">x</p>`));
  await color('elem_vs_class_order', doc('<style>.c{color:rgb(0,0,255)}p{color:rgb(255,0,0)}</style><p id=t class=c>x</p>'));
  await color('universal_zero', doc('<style>p{color:rgb(0,0,255)}*{color:rgb(255,0,0)}</style><p id=t>x</p>'));
  await color('where_zero', doc('<style>p{color:rgb(255,0,0)}:where(.x){color:rgb(0,0,255)}</style><p id=t class=x>x</p>'));
  await color('is_counts', doc('<style>p{color:rgb(255,0,0)}:is(.x){color:rgb(0,0,255)}</style><p id=t class=x>x</p>'));
  for (const [name, css] of [['pc_later', '.x{color:rgb(0,0,255)}:hover{color:rgb(255,0,0)}'], ['pc_earlier', ':hover{color:rgb(255,0,0)}.x{color:rgb(0,0,255)}'],
                             ['lvha_ok', 'a:link{color:rgb(0,0,255)}a:hover{color:rgb(255,0,0)}'], ['lvha_wrong', 'a:hover{color:rgb(255,0,0)}a:link{color:rgb(0,0,255)}']]) {
    await page.setContent(doc(`<style>${css}</style><a id=t class=x href="#x">link</a>`));
    await page.hover('#t'); R[name] = await page.evaluate(() => getComputedStyle(document.querySelector('#t')).color);
  }
  // external <link> vs internal <style>: whichever comes LATER wins
  await ctx.route('http://t.test/**', route => {
    const u = route.request().url();
    if (u.endsWith('/ext.css')) return route.fulfill({ contentType: 'text/css', body: 'p{color:rgb(255,0,0)}' });
    const link = '<link rel="stylesheet" href="/ext.css">', style = '<style>p{color:rgb(0,0,255)}</style>';
    return route.fulfill({ contentType: 'text/html', body: `<!DOCTYPE html><html><head>${u.endsWith('/a') ? link + style : style + link}</head><body><p id=t>x</p></body></html>` });
  });
  for (const [name, path] of [['link_then_style', '/a'], ['style_then_link', '/b']]) {
    await page.goto('http://t.test' + path); R[name] = await page.evaluate(() => getComputedStyle(document.querySelector('#t')).color);
  }
  // target=_blank: modern browsers imply noopener
  await ctx.route('http://a.test/**', r => r.fulfill({ contentType: 'text/html', body: '<a id=l href="http://b.test/" target="_blank">go</a>' }));
  await ctx.route('http://b.test/**', r => r.fulfill({ contentType: 'text/html', body: '<p>b</p>' }));
  await page.goto('http://a.test/');
  const [popup] = await Promise.all([ctx.waitForEvent('page'), page.click('#l')]);
  await popup.waitForLoadState(); R.blank_opener_is_null = await popup.evaluate(() => window.opener === null); await popup.close();

  // --- selectors
  const count = async (name, inner, sel) => { await page.setContent(doc(inner)); R[name] = await page.evaluate(s => [...document.querySelectorAll(s)].map(e => e.getAttribute('data-v')), sel); };
  const els = (attr, vals) => vals.map(v => `<p ${attr}="${v}" data-v="${v}"></p>`).join('');
  await count('attr_tilde', els('title', ['first post', 'para first', 'first-list', 'firstoy']), '[title~="first"]');
  await count('attr_star', els('class', ['postman', 'Aposts', 'newpost', 'other']), '[class*="post"]');
  await count('attr_pipe', els('class', ['en', 'en-US', 'english']), '[class|="en"]');
  await count('attr_caret', els('class', ['en', 'en-US', 'english', 'foo en']), '[class^="en"]');
  await count('attr_dollar', els('class', ['mytest', 'test', 'testing']), '[class$="test"]');
  await count('attr_eq', els('type', ['button', 'buttons', 'xbutton']), '[type="button"]');
  const dom = '<div id=d><p data-v=child>c</p><section><p data-v=grandchild>g</p></section></div><p data-v=sib1>1</p><p data-v=sib2>2</p><span>s</span><p data-v=sib3>3</p>';
  await count('comb_descendant', dom, 'div p'); await count('comb_child', dom, 'div > p');
  await count('comb_next', dom, 'div + p'); await count('comb_subsequent', dom, 'div ~ p');
  const li = '<ul><li data-v=1></li><li data-v=2></li><li data-v=3></li></ul><article><h2></h2><p data-v=p1></p><p data-v=p2></p></article>';
  await count('first_child', li, 'li:first-child'); await count('last_child', li, 'li:last-child'); await count('nth_odd', li, 'li:nth-child(odd)');
  await count('nth_last', li, 'li:nth-last-child(1)'); await count('first_of_type', li, 'article p:first-of-type'); await count('only_child', li, 'li:only-child');
  R.supports = await page.evaluate(() => Object.fromEntries([
    'selector(:has(img))', 'selector(:is(h1,h2))', 'selector(:where(nav a))', 'selector(::backdrop)', 'selector(::marker)', 'selector(::selection)',
    'selector(::first-line)', 'selector(::first-letter)', 'selector(:focus-visible)', 'selector(:focus-within)', 'selector(:read-write)', 'selector(:optional)',
    'selector(:target)', 'selector(:empty)', 'selector(::placeholder)', 'selector(:nth-last-child(1))',
    'transform: uppercase', 'text-transform: uppercase', 'text-align: justify', 'font: italic bolder 18px Times, serif', 'vertical-align: text-top',
    'accent-color: green', 'list-style-type: upper-roman', 'font-weight: bolder'].map(q => [q, CSS.supports(q.startsWith('selector') ? q : q.replace(/^([^:]+):(.*)$/, '($1:$2)'))])));
  await run('pseudo_content', doc('<style>.n::before{content:"Note: "}.m::before{color:red}</style><p class=n>x</p><p class=m>y</p>'),
    () => ({ withContent: getComputedStyle(document.querySelector('.n'), '::before').content, without: getComputedStyle(document.querySelector('.m'), '::before').content }));

  // --- box model, shorthands, units
  const box = style => `<div id=wrap style="width:2000px"><div id=d style="${style}"></div></div>`;
  const measure = () => { const d = document.getElementById('d'), cs = getComputedStyle(d); return { offsetW: d.offsetWidth, offsetH: d.offsetHeight, contentW: cs.width, contentH: cs.height }; };
  const common = 'height:100px;margin:3px;padding:25px 50px 75px 100px;border:5px solid gray;';
  await run('box_maxwidth', doc(box(common + 'width:50%;max-width:500px')), measure);
  await run('box_min', doc(box(common + 'width:min(50%,500px)')), measure);
  await run('box_max', doc(box(common + 'width:max(50%,500px)')), measure);
  await run('padding_shorthand', doc('<div id=d style="padding:30px 20px"></div>'), () => { const cs = getComputedStyle(d); return [cs.paddingTop, cs.paddingRight, cs.paddingBottom, cs.paddingLeft]; });
  await run('padding_four', doc('<div id=d style="padding:25px 50px 75px 100px"></div>'), () => { const cs = getComputedStyle(d); return [cs.paddingTop, cs.paddingRight, cs.paddingBottom, cs.paddingLeft]; });
  await run('center_auto', doc('<div style="width:1000px"><div id=a style="width:50%;margin:auto">x</div><div id=b style="margin:auto">y</div></div>'),
    () => { const m = id => [getComputedStyle(document.getElementById(id)).marginLeft, getComputedStyle(document.getElementById(id)).marginRight]; return { withWidth: m('a'), noWidth: m('b') }; });
  await run('display_none', doc('<div id=a>a</div><div id=h style="display:none">hidden</div><div id=n>n</div>'), () => document.getElementById('n').getBoundingClientRect().top);
  await run('visibility_hidden', doc('<div id=a>a</div><div id=h style="visibility:hidden">hidden</div><div id=n>n</div>'), () => document.getElementById('n').getBoundingClientRect().top);
  await run('baseline_top', doc('<div id=a>a</div><div id=n>n</div>'), () => document.getElementById('n').getBoundingClientRect().top);
  await run('units', doc('<div style="font-size:20px"><p id=em style="font-size:2em;padding:1em"></p><p id=pct style="font-size:200%"></p><p id=rem style="font-size:1.5rem"></p>' +
    '<p id=smaller style="font-size:smaller"></p><p id=larger style="font-size:larger"></p></div>'),
    () => { const g = (id, p = 'fontSize') => getComputedStyle(document.getElementById(id))[p]; return { em: g('em'), emPadding: g('em', 'paddingLeft'), pct: g('pct'), rem: g('rem'), smaller: g('smaller'), larger: g('larger') }; });

  // --- the block/inline example of 2-3 (the visualizer is gone, the note carries this HTML instead)
  await page.setContent(doc(input.visualizer));
  R.visualizer = await page.evaluate(() => { try {
    const top = e => Math.round(e.getBoundingClientRect().top), bot = e => Math.round(e.getBoundingClientRect().bottom);
    const q = s => document.querySelector(s), lines = e => new Set([...e.getClientRects()].map(r => Math.round(r.top))).size;
    const wrap = q('#wrap'), group = [...wrap.querySelectorAll('.g')];
    return { spanEmSameLine: top(q('#s1')) === top(q('#e1')), pBelow: top(q('#pp')) >= bot(q('#e1')),
             groupLines: new Set(group.flatMap(e => [...e.getClientRects()].map(r => Math.round(r.top)))).size,
             divFull: q('#dv').getBoundingClientRect().width === wrap.getBoundingClientRect().width, lastBelowDiv: top(q('#last')) >= bot(q('#dv')) };
  } catch (e) { return { missing: String(e.message) }; } });

  R.cases = [];
  for (const c of (input.cases || [])) {
    await page.setContent(doc(`<style>${c.css}</style>${c.html}`));
    R.cases.push(await page.evaluate(() => getComputedStyle(document.querySelector('p')).color));
  }
  // --- screenshots of the notes' own HTML (so GitHub shows exactly what a browser renders)
  for (const sh of (input.shots || [])) {
    const p2 = await b.newPage({ viewport: { width: sh.width, height: 10 }, deviceScaleFactor: 2 });
    await p2.setContent(`<!DOCTYPE html><html><head><meta charset="utf-8"><style>body{margin:0;padding:10px 14px;font:16px/1.5 -apple-system,'Segoe UI',Helvetica,Arial,sans-serif;background:#fff;color:#000}${sh.css || ''}</style></head><body>${sh.html}</body></html>`);
    await p2.screenshot({ path: sh.path, fullPage: true });
  }
  // --- CSS syntax of every ```css snippet
  R.css = await page.evaluate(items => items.map(it => ({ where: it.where,
      badSel: it.selectors.filter(s => !CSS.supports(`selector(${s})`)),
      badDecl: it.decls.filter(([p, v]) => !CSS.supports(p, v)).map(d => d.join(': ')) })), input.css);
  console.log(JSON.stringify(R));
  await b.close();
})();
"""


def css_items():
    """Every declaration and selector of every ```css block and <style> element in the notes."""
    items = []
    for f in md_files():
        t = f.read_text(encoding="utf-8")
        srcs = [(ln, b) for ln, b in blocks(t, {"css"})]
        for ln, b in blocks(t, {"html"}):
            for m in re.finditer(r"<style[^>]*>(.*?)</style>", b, re.S):
                srcs.append((ln, m.group(1)))
        for ln, css in srcs:
            css = re.sub(r"/\*.*?\*/", "", css, flags=re.S)
            sels, decls = [], []
            for m in re.finditer(r"([^{}]+)\{([^{}]*)\}", css):
                for s in re.split(r",(?![^()]*\))", m.group(1)):
                    s = s.strip()
                    if s and not s.startswith("@") and not s.startswith("selector"):      # 'selector::pseudo-element' is a syntax template
                        sels.append(s)
                for d in m.group(2).split(";"):
                    if ":" in d:
                        p, v = d.split(":", 1)
                        decls.append([p.strip(), re.sub(r"\s*!important\s*$", "", v.strip())])
            items.append({"where": f"{f.name}:{ln}", "selectors": sels, "decls": decls})
    return items


def case_examples():
    """(css, html) pairs under each '#### Case N' heading of 2-6, in order."""
    t = note("2-6-css-selector-specificity.md")
    out = []
    for part in re.split(r"^#### Case ", t, flags=re.M)[1:]:
        part = part.split("\n###", 1)[0]
        css = [b for _, b in blocks(part, {"css"})]
        html = [b for _, b in blocks(part, {"html"})]
        out += [{"css": c, "html": h} for c, h in zip(css, html)]
    return out


def run_browser():
    node = shutil.which("node")
    if not node:
        return None
    t = note("2-3-html-basics.md")
    vis = [b for _, b in blocks(t, {"html"}) if 'id="wrap"' in b]
    visualizer = vis[0] if vis else "<div id=wrap></div>"
    with tempfile.TemporaryDirectory() as d:
        shots = []
        if os.environ.get("MAKE_SHOT"):                     # regenerate the two note images from the notes' own HTML
            fmt = "\n".join(re.findall(r"^<p>.*</p>$", "\n".join(b for _, b in blocks(note("2-4-html-elements.md"), {"html"})), re.M)[:9])
            shots = [{"html": fmt, "path": str(ROOT / "static" / "html-text-formatting.png"), "width": 360, "css": "p{margin:0 0 4px}"},
                     {"html": visualizer, "path": str(ROOT / "static" / "html-block-inline.png"), "width": 360,
                      "css": "span,em,strong,a{outline:1px dashed #d33}div,p{outline:1px solid #36c}#wrap{margin:4px 0 4px 4px}"}]
        Path(d, "in.json").write_text(json.dumps({"visualizer": visualizer, "css": css_items(), "shots": shots, "cases": case_examples()}))
        Path(d, "b.js").write_text(BROWSER_JS)
        env = dict(os.environ, NODE_PATH=subprocess.run(["npm", "root", "-g"], capture_output=True, text=True).stdout.strip())
        p = subprocess.run([node, str(Path(d, "b.js")), str(Path(d, "in.json"))], capture_output=True, text=True, env=env, timeout=240)
        if p.returncode:
            raise RuntimeError(p.stderr.strip().splitlines()[-1] if p.stderr.strip() else "node failed")
        return json.loads(p.stdout.strip().splitlines()[-1])


def rgb(r, g, b):
    return f"rgb({r}, {g}, {b})"


RED, BLUE, GREEN = rgb(255, 0, 0), rgb(0, 0, 255), rgb(0, 128, 0)


# ---- 2-3 html basics --------------------------------------------------------
def doctype(B):
    t = note("2-3-html-basics.md")
    good = has(t, r"standards mode") and not has(t, r"Declares the document type and version of HTML")
    return B["compat_doctype"] == "CSS1Compat" and B["compat_none"] == "BackCompat" and good, (
        f"document.compatMode: with <!DOCTYPE html> = {B['compat_doctype']}, without = {B['compat_none']} (quirks); HTML5 has no versions in the doctype; note says 'standards mode': {good}")


def html_living_standard():
    t = note("2-3-html-basics.md")
    return has(t, r"Living Standard") and not has(t, r"HTML5 is the current standard"), "HTML is a WHATWG Living Standard (HTML5 was the last numbered version)"


def void_not_selfclosing(B):
    t = note("2-3-html-basics.md")
    good = has(t, r"no (such thing as )?self-closing|not self-closing|slash .{0,40}(ignored|no effect)") and not has(t, r"They are self-closing")
    return B["div_selfclose"] is True and good, (
        f"`<div/><p>x</p>` -> the <p> ends up INSIDE the div ({B['div_selfclose']}), so '/>' does not close non-void elements; the Nu validator calls it an error; "
        f"note no longer calls void elements 'self-closing' and explains the slash: {good}")


def inline_width(B):
    sp, im, ib = B["inline_width"]["span"], B["inline_width"]["img"], B["inline_width"]["inlineBlock"]
    t = note("2-3-html-basics.md")
    good = has(t, r"replaced") and has(t, r"<img>.{0,200}(width|height)")
    return sp[0] < 100 and sp[1] < 80 and im == [300, 200] and ib == [100, 50] and B["display"]["img"] == "inline" and good, (
        f"<span style='width:300px;height:80px'> is {sp[0]:.0f}x{sp[1]:.0f} px (ignored); <img> (display:{B['display']['img']}) with width/height = {im}; "
        f"inline-block span = {ib}; note says width/height are ignored by inline NON-replaced elements but <img> (replaced) accepts them: {good}")


def block_inline_defaults(B):
    d = B["display"]
    block = all(d[t] == "block" for t in ("div", "p", "h1", "form", "section", "ul"))
    inline = all(d[t] == "inline" for t in ("span", "a", "img", "strong", "em"))
    w = B["block_width"]
    return block and inline and d["li"] == "list-item" and d["input"] == "inline-block" and w["div"] == 800 and w["p"] == 800 and w["span"] < 100, (
        f"computed display: {d}; <div>/<p> are 800px wide in an 800px parent, <span> {w['span']:.0f}px")


def visualizer_example(B):
    v = B["visualizer"]
    t = note("2-3-html-basics.md")
    if "missing" in v:
        return False, f"the note has no runnable block/inline example (needs #wrap, #s1, #e1, #pp, .g, #dv, #last): {v['missing']}"
    good = any('id="wrap"' in b for _, b in blocks(t, {"html"}))
    return v["spanEmSameLine"] and v["pBelow"] and v["groupLines"] >= 2 and v["divFull"] and v["lastBelowDiv"] and good, (
        f"the HTML now shown in the note reproduces the 4 questions: SPAN+EM same line {v['spanEmSameLine']}, P on a new line {v['pBelow']}, "
        f"inline group wraps onto {v['groupLines']} lines, DIV full width {v['divFull']}, last SPAN after the DIV {v['lastBelowDiv']}; note carries the example: {good}")


# ---- 2-4 html elements ------------------------------------------------------
def list_type_attr():
    t = note("2-4-html-elements.md")
    good = has(t, r"`<ul>`.{0,60}(obsolete|deprecated)") and has(t, r"`<ol>`.{0,120}(valid|still|not deprecated|not obsolete)")
    bad = has(t, r"The `type` attribute for lists is deprecated in HTML5")
    return good and not bad, f"(Nu validator) <ol type=A start=5> is VALID, <ul type=circle> is obsolete; note distinguishes them: {good}; old blanket statement present: {bad}"


def noopener(B):
    t = note("2-4-html-elements.md")
    good = has(t, r"already (imply|implies)|implied by default|implicit")
    return B["blank_opener_is_null"] is True and good, f"popup opened via target=_blank WITHOUT rel -> window.opener === null: {B['blank_opener_is_null']}; note says modern browsers already imply noopener: {good}"


def img_size_advice():
    t = note("2-4-html-elements.md")
    bad = has(t, r"Better practice is to use CSS for styling images rather than using the `height` and `width` attributes")
    good = has(t, r"layout shift|reserve")
    return not bad and good, f"width/height attributes let the browser reserve space before the image loads (avoids layout shift), so 'prefer CSS instead' is misleading: old text {bad}; fixed text {good}"


def html_cross_refs():
    t = note("2-4-html-elements.md")
    return not has(t, r"2-html-basics\.md"), "link target is 2-3-html-basics.md (checked again by the link-resolver below)"


# ---- 2-5 tables -------------------------------------------------------------
def table_facts(B):
    th = B["th_defaults"]
    t = note("2-5-html-tables.md")
    tb = B["implicit_tbody"]
    good = has(t, r"automatically (insert|add)|inserts? an implicit `?<tbody>") and not has(t, r"know as")
    return (th["thWeight"] == "700" and th["thAlign"] in ("center", "-internal-center") and th["tdWeight"] == "400" and th["collapse"] == "separate"
            and tb["first"] == "TBODY" and tb["odd"] == ["r1", "r3"] and tb["direct"] == 0 and good), (
        f"<th> default: weight {th['thWeight']}, align {th['thAlign']}; <td> weight {th['tdWeight']}; border-collapse default = {th['collapse']}; "
        f"the parser inserts <tbody> itself (table's first child is {tb['first']}, so `table > tr` matches {tb['direct']} rows while `table tr:nth-child(odd)` works: {tb['odd']}); "
        f"note mentions the implicit <tbody> and the 'know as' typo is fixed: {good}")


# ---- 2-6 css ----------------------------------------------------------------
def cascade(B):
    ok = (B["case1_later"] == BLUE and B["case1_swapped"] == RED and B["case2_id_vs_class"] == RED and B["case3_inline"] == BLUE
          and B["case4_important"] == BLUE and B["case5_id_important"] == RED and B["case5_equal_later"] == RED and B["case5_inline_important"] == BLUE)
    t = note("2-6-css-selector-specificity.md")
    good = all(has(t, p) for p in (r"Case 1", r"Case 2", r"Case 3", r"Case 4", r"Case 5")) and not has(t, r"<CSS-specificity")
    return ok and good, (f"case 1 (same specificity, later wins) {B['case1_later']} / swapped {B['case1_swapped']}; case 2 ID beats class {B['case2_id_vs_class']}; "
                         f"case 3 inline beats ID {B['case3_inline']}; case 4 !important beats inline+ID {B['case4_important']}; case 5 ID !important beats class !important {B['case5_id_important']}, "
                         f"equal !important -> later {B['case5_equal_later']}, inline !important beats sheet !important {B['case5_inline_important']}; note carries runnable examples for all 5 cases: {good}")


def case_examples_render(B):
    want = {"red": RED, "blue": BLUE, "green": GREEN}
    cases = case_examples()
    bad, rows = [], []
    for c, got in zip(cases, B["cases"]):
        word = re.search(r"(\w+) text</p>", c["html"]).group(1).lower()
        rows.append(f"{word}->{'ok' if got == want[word] else got}")
        if got != want[word]:
            bad.append((word, got))
    return len(cases) == 6 and not bad, f"the {len(cases)} css+html examples under 'Case 1..5' of the note, rendered in Chromium: {', '.join(rows)}"


def specificity_is_not_a_sum(B):
    t = note("2-6-css-selector-specificity.md")
    good = has(t, r"not (a|just a) (sum|number)|three-part|\(ids, classes, elements\)|IDs.{0,40}classes.{0,40}elements") and has(t, r"pseudo-classes?.{0,60}(class|same level)")
    return (B["many_classes_vs_id"] == RED and B["elem_vs_class_order"] == BLUE and B["universal_zero"] == BLUE and B["pc_later"] == RED and B["pc_earlier"] == BLUE
            and B["where_zero"] == RED and B["is_counts"] == BLUE and good), (
        f"30 classes still lose to ONE id ({B['many_classes_vs_id']}); class beats element regardless of order ({B['elem_vs_class_order']}); `*` has zero specificity ({B['universal_zero']}); "
        f":hover ties with a class (later wins: {B['pc_later']} / {B['pc_earlier']}); :where() adds nothing ({B['where_zero']}), :is() does ({B['is_counts']}); "
        f"note explains specificity as (IDs, classes/attributes/pseudo-classes, elements) and not a decimal sum: {good}")


def internal_vs_external(B):
    t = note("2-6-css-selector-specificity.md")
    bad = has(t, r"so inline wins") or has(t, r"/\* inline css \*/")
    good = has(t, r"internal (style )?wins") and has(t, r"(later|last)")
    return B["link_then_style"] == BLUE and B["style_then_link"] == RED and not bad and good, (
        f"<link> then <style> -> {B['link_then_style']} (internal wins); <style> then <link> -> {B['style_then_link']} (external wins): same specificity, the LATER one wins; "
        f"note no longer calls the internal <style> rule 'inline' and explains the order: {good}; old wording present: {bad}")


def attribute_selectors(B):
    ok = (B["attr_tilde"] == ["first post", "para first"] and B["attr_star"] == ["postman", "Aposts", "newpost"] and B["attr_pipe"] == ["en", "en-US"]
          and B["attr_caret"] == ["en", "en-US", "english"] and B["attr_dollar"] == ["mytest", "test"] and B["attr_eq"] == ["button"])
    t = note("2-6-css-selector-specificity.md")
    good = has(t, r"whole (attribute|class) (value|string)|entire (attribute|class)")
    return ok and good, (f"~= {B['attr_tilde']}; *= {B['attr_star']}; |= {B['attr_pipe']} (not 'english'); ^= {B['attr_caret']} (class=\"foo en\" does not match: it tests the whole attribute string); "
                         f"$= {B['attr_dollar']}; = {B['attr_eq']}; note explains the whole-string behaviour: {good}")


def combinators(B):
    ok = (B["comb_descendant"] == ["child", "grandchild"] and B["comb_child"] == ["child"] and B["comb_next"] == ["sib1"] and B["comb_subsequent"] == ["sib1", "sib2", "sib3"])
    return ok, f"`div p` {B['comb_descendant']}; `div > p` {B['comb_child']}; `div + p` {B['comb_next']}; `div ~ p` {B['comb_subsequent']}"


def box_model(B):
    mw, mn, mx = B["box_maxwidth"], B["box_min"], B["box_max"]
    t = note("2-6-css-selector-specificity.md")
    bad = has(t, r"EQUIVALENT TO width: max\(50%, 500px\)") or has(t, r"= 500px \(as we set max-width else 660 px\)")
    good = has(t, r"min\(50%, 500px\)") and has(t, r"500px.{0,60}150px.{0,60}10px.{0,60}= 660px")
    return (mw["offsetW"] == 660 and mw["offsetH"] == 210 and mw["contentW"] == "500px" and mn["offsetW"] == 660 and mx["offsetW"] == 1160
            and B["boxsizing"] == "content-box" and B["padding_shorthand"] == ["30px", "20px", "30px", "20px"] and B["padding_four"] == ["25px", "50px", "75px", "100px"]
            and not bad and good), (
        f"in a 2000px parent: width:50% + max-width:500px -> content {mw['contentW']}, box {mw['offsetW']}x{mw['offsetH']} (500+150+10 = 660 wide, 100+100+10 = 210 tall); "
        f"max-width acts like min(50%, 500px) ({mn['offsetW']}px) NOT max(50%, 500px) ({mx['offsetW']}px); box-sizing default {B['boxsizing']}; "
        f"padding:30px 20px -> {B['padding_shorthand']}; four values are top right bottom left -> {B['padding_four']}; note fixed: {good}; old wrong text present: {bad}")


def display_none(B):
    return B["display_none"] == B["baseline_top"] and B["visibility_hidden"] > B["baseline_top"], (
        f"display:none -> next block starts at y={B['display_none']} (same as with no element: {B['baseline_top']}); visibility:hidden keeps the space (y={B['visibility_hidden']})")


def link_order(B):
    t = note("2-6-css-selector-specificity.md")
    good = has(t, r"hover.{0,80}(before|after).{0,120}(override|wins|ignored)|LoVe\s*HAte|LVHA")
    return B["lvha_ok"] == RED and B["lvha_wrong"] == BLUE and good, (
        f":link -> :hover order gives {B['lvha_ok']} on hover; the wrong order (:hover first) gives {B['lvha_wrong']} -- the later equal-specificity :link rule wins; note explains WHY order matters: {good}")


def center_auto(B):
    c = B["center_auto"]
    return c["withWidth"] == ["250px", "250px"] and c["noWidth"] == ["0px", "0px"], f"margin:auto + width:50% in 1000px -> margins {c['withWidth']}; margin:auto without a width -> {c['noWidth']} (nothing to centre)"


def css_units(B):
    u = B["units"]
    t = note("2-7-css-extra.md")
    good = has(t, r"em.{0,160}(own|element's own) font[- ]size") and not has(t, r"uni`t")
    return (u["em"] == "40px" and u["emPadding"] == "40px" and u["pct"] == "40px" and u["rem"] == "24px" and float(u["smaller"][:-2]) < 20 < float(u["larger"][:-2]) and good), (
        f"parent 20px: font-size:2em = {u['em']}, 200% = {u['pct']}; padding:1em on that 40px element = {u['emPadding']} (em = the element's OWN font-size for every property except font-size); 1.5rem = {u['rem']}; "
        f"smaller = {u['smaller']}, larger = {u['larger']}; note says so + stray backticks removed: {good}")


# ---- 2-7 css-extra ----------------------------------------------------------
def property_names(B):
    s = B["supports"]
    t = note("2-7-css-extra.md")
    good = has(t, r"`text-transform`") and has(t, r"text-align: justify") and not has(t, r"`color`, `text-align`, `transform`")
    return (s["transform: uppercase"] is False and s["text-transform: uppercase"] and s["text-align: justify"] and s["font: italic bolder 18px Times, serif"]
            and s["vertical-align: text-top"] and good), (
        f"`transform: uppercase` is INVALID ({not s['transform: uppercase']}) -- the property is text-transform ({s['text-transform: uppercase']}); `justify` is a value of text-align ({s['text-align: justify']}); note fixed: {good}")


def selectors_exist(B):
    s = B["supports"]
    keys = [k for k in s if k.startswith("selector(")]
    pc = B["pseudo_content"]
    t = note("2-7-css-extra.md")
    good = has(t, r"::before.{0,200}content")
    return all(s[k] for k in keys) and pc["withContent"] == '"Note: "' and pc["without"] in ("none", "normal") and good, (
        f"all {len(keys)} pseudo-class / pseudo-element selectors used in the notes are valid in Chromium; ::before with content -> {pc['withContent']}, without -> {pc['without']} (nothing generated)")


def structural_pseudo(B):
    ok = (B["first_child"] == ["1"] and B["last_child"] == ["3"] and B["nth_odd"] == ["1", "3"] and B["nth_last"] == ["3"] and B["first_of_type"] == ["p1"] and B["only_child"] == [])
    return ok, f"li:first-child {B['first_child']}, :last-child {B['last_child']}, :nth-child(odd) {B['nth_odd']}, :nth-last-child(1) {B['nth_last']}, article p:first-of-type {B['first_of_type']}, :only-child {B['only_child']}"


def bootstrap_sri():
    path = os.environ.get("BOOTSTRAP_CSS")
    if not (path and Path(path).exists()):
        SKIPPED.append("Bootstrap integrity hash skipped (set BOOTSTRAP_CSS=.../bootstrap/dist/css/bootstrap.min.css from `npm install bootstrap@5.3.5`)")
        return None
    sri = "sha384-" + base64.b64encode(hashlib.sha384(Path(path).read_bytes()).digest()).decode()
    t = note("2-7-css-extra.md")
    return sri in t and "bootstrap@5.3.5" in t, f"sha384 of bootstrap@5.3.5 bootstrap.min.css = {sri[:30]}...; it is the integrity value in the note: {sri in t}"


# --------------------------------------------------------------------------- #
# HTML validity with the Nu validator
# --------------------------------------------------------------------------- #
def nu_validate():
    jar, java = os.environ.get("VNU_JAR"), shutil.which("java")
    if not (jar and Path(jar).exists() and java):
        SKIPPED.append("Nu HTML validator skipped (set VNU_JAR=.../vnu.jar, needs java; `npm install vnu-jar`)")
        return None
    tpl = '<!DOCTYPE html>\n<html lang="en">\n<head><meta charset="utf-8"><title>t</title></head>\n<body>\n%s\n</body>\n</html>\n'
    with tempfile.TemporaryDirectory() as d:
        index = {}
        for f in md_files():
            for ln, body in blocks(f.read_text(encoding="utf-8"), {"html"}):
                full = re.match(r"\s*<!DOCTYPE", body, re.I) is not None
                if not full and re.search(r"<html|<head|<body", body):
                    continue                                   # deliberate document fragment (2-6 'How to add CSS')
                name = f"{f.name[:5]}_L{ln}.html"
                Path(d, name).write_text(body if full else tpl % body, encoding="utf-8")
                index[name] = (f.name, ln, full)
        p = subprocess.run([java, "-jar", jar, "--format", "json", "--skip-non-html", *sorted(Path(d).glob("*.html"))], capture_output=True, text=True)
        msgs = json.loads(p.stderr[p.stderr.index("{"):] if "{" in p.stderr else p.stdout)["messages"]
    errors = [f"{index[m['url'].split('/')[-1]][0]}:{index[m['url'].split('/')[-1]][1]} {m['message'][:90]}" for m in msgs if m["type"] == "error"]
    return not errors, f"{len(index)} ```html snippets validated against the HTML standard; errors: {errors or 'none'}"


def nu_obsolete_claims():
    jar, java = os.environ.get("VNU_JAR"), shutil.which("java")
    if not (jar and Path(jar).exists() and java):
        return None
    T = '<!DOCTYPE html><html lang="en"><head><meta charset="utf-8"><title>t</title></head><body>%s</body></html>'
    cases = {
        "ol_type": '<ol type="A" start="5"><li>x</li></ol>', "ul_type": '<ul type="circle"><li>x</li></ul>', "a_name": '<a name="top" href="#">x</a>',
        "table_border": '<table border="1"><tr><td>x</td></tr></table>', "table_cellpadding": '<table cellpadding="4"><tr><td>x</td></tr></table>',
        "table_bgcolor": '<table bgcolor="red"><tr><td>x</td></tr></table>', "td_align": '<table><tr><td align="center">x</td></tr></table>',
        "tbody_align": '<table><tbody align="center"><tr><td>x</td></tr></tbody></table>', "tfoot_last": '<table><thead><tr><th>a</th></tr></thead><tbody><tr><td>b</td></tr></tbody><tfoot><tr><td>c</td></tr></tfoot></table>',
        "th_scope": '<table><tr><th scope="rowgroup">x</th></tr></table>', "img_wh": '<img src="a.png" alt="a" width="300" height="200">', "u_b_i": "<p><u>x</u><b>b</b><i>i</i><small>s</small><mark>m</mark></p>",
    }
    with tempfile.TemporaryDirectory() as d:
        for k, v in cases.items():
            Path(d, k + ".html").write_text(T % v, encoding="utf-8")
        p = subprocess.run([java, "-jar", jar, "--format", "json", *sorted(Path(d).glob("*.html"))], capture_output=True, text=True)
        msgs = json.loads(p.stderr[p.stderr.index("{"):])["messages"]
    by = {}
    for m in msgs:
        by.setdefault(m["url"].split("/")[-1][:-5], []).append(m["message"])
    obsolete = lambda k: any("obsolete" in x or "never allowed" in x for x in by.get(k, []))
    errors = lambda k: [x for x in by.get(k, []) if "obsolete" not in x]
    ok = (not by.get("ol_type") and obsolete("ul_type") and obsolete("a_name") and obsolete("table_border") and obsolete("table_cellpadding") and obsolete("table_bgcolor")
          and obsolete("td_align") and obsolete("tbody_align") and not by.get("tfoot_last") and not by.get("th_scope") and not by.get("img_wh") and not by.get("u_b_i"))
    t = note("2-5-html-tables.md")
    good = has(t, r"tbody.{0,200}align") or True
    return ok, (f"valid: <ol type start>, tfoot after tbody, th scope=rowgroup, img width/height, <u><b><i><small><mark>; obsolete: ul type, a name, table border / cellpadding / bgcolor, td/tbody align "
                f"(<ol type> is NOT obsolete)")


def css_syntax(B):
    bad = [f"{i['where']}: selectors {i['badSel']} declarations {i['badDecl']}" for i in B["css"] if i["badSel"] or i["badDecl"]]
    n = sum(len(i["selectors"]) + len(i["decls"]) for i in css_items())
    return not bad, f"{n} selectors/declarations in {len(B['css'])} CSS snippets checked with CSS.supports(); invalid: {bad or 'none'}"


# --------------------------------------------------------------------------- #
# text-level wording checks
# --------------------------------------------------------------------------- #
def wording_checks():
    bad = {
        "2-1-ascii-unicode.md": [r"youtube\.com/embed/"],
        "2-2-number-systems.md": [r"<NumberSystemConverter", r"`A=10,; B=11"],
        "2-5-html-tables.md": [r"know as", r"tags\.Table"],
        "2-6-css-selector-specificity.md": [r"reusable <class="],
        "2-7-css-extra.md": [r"th`e parent", r"uni`t"],
    }
    found = [(f, p) for f, ps in bad.items() for p in ps if has(note(f), p)]
    return not found, f"known typos / garbled phrases still present: {found or 'none'}"


# --------------------------------------------------------------------------- #
# markdown / GitHub hygiene (as for week5, week0, week1)
# --------------------------------------------------------------------------- #
def no_vitepress_syntax():
    found = []
    for f in md_files():
        for i, line in enumerate(f.read_text(encoding="utf-8").splitlines(), 1):
            if re.match(r"^\s*:::|^\s*== ?\S|^\s*```\s*\w+\s*\[", line) or re.search(r"<[A-Z][\w-]*[^>]*/>", line) or re.search(r"<(NumberSystemConverter|CSS-specificity|pseudo-class|block-inline-visualizer)", line):
                found.append(f"{f.name}:{i}")
    return not found, f"VitePress-only syntax (::: / == / ```lang[Label] / Vue components): {found or 'none'}"


def no_stripped_html():
    found = []
    for f in md_files():
        t = strip_fences(f.read_text(encoding="utf-8"))
        t = re.sub(r"<!--.*?-->", "", t, flags=re.S)
        t = re.sub(r"`[^`\n]*`", "", t)                  # inline code spans show tags, they do not render them
        for m in re.finditer(r"<(?!/)[^>]*(\sstyle\s*=|\sclass\s*=)[^>]*>|&emsp;", t):
            found.append(f"{f.name}: {m.group(0)[:50]}")
    return not found, f"HTML that GitHub strips (style=, class=, &emsp;) outside code blocks: {found or 'none'}"


def alerts_valid():
    bad = []
    for f in md_files():
        for i, line in enumerate(f.read_text(encoding="utf-8").splitlines(), 1):
            m = re.match(r"^> \[!(\w+)\]\s*$", line)
            if m and m.group(1) not in {"NOTE", "TIP", "IMPORTANT", "WARNING", "CAUTION"}:
                bad.append(f"{f.name}:{i}")
            if re.match(r"^>\s*\[!\w+\]\S", line):
                bad.append(f"{f.name}:{i} text after [!TYPE]")
    return not bad, f"invalid GitHub alert syntax: {bad or 'none'}"


def details_balanced():
    bad = []
    for f in md_files():
        t = f.read_text(encoding="utf-8")
        o, c = len(re.findall(r"<details>", t)), len(re.findall(r"</details>", t))
        if o != c:
            bad.append(f"{f.name}: {o} <details> vs {c} </details>")
        for m in re.finditer(r"<summary>(.*?)</summary>", t, re.S):
            if "`" in m.group(1):
                bad.append(f"{f.name}: backticks in <summary>")
    return not bad, f"unbalanced <details> / backticks in <summary>: {bad or 'none'}"


def links_resolve():
    bad = []
    for f in md_files():
        text = re.sub(r"```.*?```", "", f.read_text(encoding="utf-8"), flags=re.S)
        for m in re.finditer(r"!?\[[^\]]*\]\(([^)\s]+)\)", text):
            url = m.group(1)
            if re.match(r"(https?:|mailto:|#)", url):
                continue
            path, _, anchor = url.partition("#")
            target = (f.parent / path).resolve()
            if not target.exists():
                bad.append(f"{f.name}: {url} (file not found)")
            elif anchor and target.suffix == ".md":
                slugs = {github_slug(h) for h in re.findall(r"^#{1,6}\s+(.*)$", target.read_text(encoding="utf-8"), re.M)}
                if anchor not in slugs:
                    bad.append(f"{f.name}: {url} (no such heading)")
        for m in re.finditer(r'<img[^>]*src="([^"]+)"', text):
            if not m.group(1).startswith("http") and not (f.parent / m.group(1)).resolve().exists():
                bad.append(f"{f.name}: image {m.group(1)}")
    return not bad, f"local links / anchors / images that do not resolve: {bad or 'none'}"


def fences_clean():
    bad = []
    for f in md_files():
        open_ = False
        for i, line in enumerate(f.read_text(encoding="utf-8").splitlines(), 1):
            m = re.match(r"^(\s*)```(.*)$", line)
            if not m:
                continue
            if not open_:
                open_ = True
                if "[" in m.group(2) or m.group(2).startswith(" "):
                    bad.append(f"{f.name}:{i} {line!r}")
            else:
                open_ = False
                if m.group(2).strip():
                    bad.append(f"{f.name}:{i} closing fence {line!r}")
        if open_:
            bad.append(f"{f.name}: unclosed fence")
    return not bad, f"labelled / badly closed / unclosed fences: {bad or 'none'}"


def youtube_links():
    ok = re.compile(r"https://(?:youtu\.be/[\w-]{11}|www\.youtube\.com/watch\?v=[\w-]{11})(?:[?&][\w=&-]*)?$")
    bad = [(f.name, u) for f in md_files() for u in re.findall(r"https?://(?:www\.)?youtu[^\s)>\]]*", f.read_text(encoding="utf-8")) if not ok.match(u)]
    return not bad, f"YouTube links not in youtu.be/<id> or watch?v=<id> form: {bad or 'none'}"


def text_screenshot_exists():
    ps = [ROOT / "static" / "html-text-formatting.png", ROOT / "static" / "html-block-inline.png"]
    refs = "html-text-formatting.png" in note("2-4-html-elements.md") and "html-block-inline.png" in note("2-3-html-basics.md")
    return all(p.exists() and p.stat().st_size > 2000 for p in ps) and refs, f"the 'Output' of the text-formatting example and the block/inline example are real Chromium renderings of the notes' own HTML (GitHub would drop <u>, <mark>, ... ): files exist {[p.exists() for p in ps]}, referenced from the notes {refs}"


# --------------------------------------------------------------------------- #
if __name__ == "__main__":
    U, N, H, E, T, C, X = ("2-1-ascii-unicode.md", "2-2-number-systems.md", "2-3-html-basics.md", "2-4-html-elements.md",
                           "2-5-html-tables.md", "2-6-css-selector-specificity.md", "2-7-css-extra.md")
    print("=" * 78 + "\nWeek 2 claim checker\n" + "=" * 78 + "\n")
    check(U, "ASCII ranges / bit patterns; '!@#...' are plain ASCII, real extended characters need Latin-1-style encodings", ascii_facts)
    check(U, "code points of 'a', 'अ', 😀; Unicode has 1,114,112 code points (U+0000..U+10FFFF), not 2^32", unicode_facts)
    check(U, "Problem 1 bit counts (160,000 / 40,000 / 35,000 / 30,000); 'A' in UCS-4 wastes 25 bits, not 32", problem_one)
    check(U, "UTF-8 table (lengths, lead-byte prefixes, ranges), the surrogate gap, UTF-16 / UTF-32 sizes", utf8_table)
    check(N, "every worked conversion and exercise answer is arithmetically right (incl. 5 x 8^2 = 320)", number_systems)

    try:
        B = run_browser()
    except Exception as e:
        B = None
        print(f"[browser] could not run: {e}\n")
    if B is None:
        SKIPPED.append("all headless-Chromium checks skipped (needs node + playwright)")
    else:
        check(H, "<!DOCTYPE html> switches on standards mode (no HTML 'version'); HTML is a Living Standard", lambda: doctype(B))
        check(H, "HTML is a Living Standard, not 'HTML5 is the current standard'", html_living_standard)
        check(H, "void elements are not 'self-closing'; '/>' on <div/> does nothing", lambda: void_not_selfclosing(B))
        check(H, "width/height do not apply to inline non-replaced elements, but do to <img> (replaced) and inline-block", lambda: inline_width(B))
        check(H, "default display values: block / inline / list-item / inline-block (input)", lambda: block_inline_defaults(B))
        check(H, "the block-vs-inline explanation is backed by an example the reader can run", lambda: visualizer_example(B))
        check(E, "<ol type> is valid HTML5, only <ul type> is obsolete", list_type_attr)
        check(E, "target=_blank already implies noopener in modern browsers", lambda: noopener(B))
        check(E, "width/height attributes on <img> are recommended (layout shift), not discouraged", img_size_advice)
        check(E, "cross-reference points to the real file name", html_cross_refs)
        check(T, "<th> bold+centred, separate borders by default, the parser inserts <tbody>", lambda: table_facts(B))
        check(C, "cascade cases 1-5 (order, ID vs class, inline, !important, equal !important)", lambda: cascade(B))
        check(C, "the note's own Case 1-5 examples render the colour each one claims", lambda: case_examples_render(B))
        check(C, "specificity is (IDs, classes/attrs/pseudo-classes, elements), not a sum; `*` = 0; :where = 0, :is = argument", lambda: specificity_is_not_a_sum(B))
        check(C, "<link> vs <style>: the LATER rule wins (internal is not 'inline')", lambda: internal_vs_external(B))
        check(C, "attribute selectors ~= *= |= ^= $= = match exactly what the comments say", lambda: attribute_selectors(B))
        check(C, "combinators: descendant / child / next sibling / subsequent siblings", lambda: combinators(B))
        check(C, "box model: max-width is min(50%,500px), total box 660 x 210, padding order TRBL", lambda: box_model(B))
        check(C, "display:none takes no space (visibility:hidden does)", lambda: display_none(B))
        check(C, "link pseudo-class order matters because equal-specificity rules: the later wins", lambda: link_order(B))
        check(X, "margin:auto centres a block only if it has a width", lambda: center_auto(B))
        check(X, "em / % / rem / smaller / larger behave as described", lambda: css_units(B))
        check(X, "`text-transform` (not `transform`); `text-align: justify`", lambda: property_names(B))
        check(X, "pseudo-element / pseudo-class selectors exist; ::before needs content", lambda: selectors_exist(B))
        check(X, ":first-child / :last-child / :nth-child / :nth-last-child / :first-of-type / :only-child", lambda: structural_pseudo(B))
        check("week2/*.md", "every declaration and selector in every ```css / <style> snippet is valid CSS", lambda: css_syntax(B))

    nu = nu_validate()
    if nu is not None:
        check("week2/*.md", "every ```html snippet is valid HTML (Nu validator)", lambda: nu)
        check(E + ", " + T, "obsolete/valid attribute claims (type, name, border, cellpadding, bgcolor, align, tfoot order, scope)", nu_obsolete_claims)
    sri = bootstrap_sri()
    if sri is not None:
        check(X, "Bootstrap 5.3.5 integrity hash is correct", lambda: sri)
    check("week2/*.md", "no typos / garbled phrases / stale component names", wording_checks)
    check(E + ", " + H, "the rendered outputs shown in the notes are real screenshots (static/html-text-formatting.png, html-block-inline.png)", text_screenshot_exists)
    check("week2/*.md", "no VitePress-only syntax (:::, ==, ```lang[label], Vue components)", no_vitepress_syntax)
    check("week2/*.md", "no HTML that GitHub strips (style=, class=, &emsp;) outside code blocks", no_stripped_html)
    check("week2/*.md", "GitHub alerts written correctly", alerts_valid)
    check("week2/*.md", "<details> balanced, no backticks in <summary>", details_balanced)
    check("week2/*.md", "every local link, #anchor and image resolves", links_resolve)
    check("week2/*.md", "code fences are labelled/closed cleanly", fences_clean)
    check("week2/*.md", "YouTube links are watch links", youtube_links)

    wrong = [f for ok, f in RESULTS if not ok]
    print("=" * 78)
    print(f"{len(RESULTS)} checks, {len(RESULTS) - len(wrong)} OK, {len(wrong)} WRONG")
    if wrong:
        print("files with WRONG statements:", ", ".join(sorted(set(wrong))))
    print("\nNOT VERIFIABLE HERE (kept because they are standard, but not executed):")
    for s in SKIPPED + [
        "::first-line / ::first-letter restricted to block containers and to a limited property list (CSS Pseudo-Elements spec; the property lists are not exercised)",
        ":visited only allows colour properties (a privacy rule: getComputedStyle deliberately hides it)",
        "Presentational / procedural / descriptive markup definitions and their example languages (terminology, not executable)",
        "external images (blog.gcwizard.net, dotnettutorials.net, hashnode) and the MDN / W3Schools / YouTube / Google Fonts links (blocked from this sandbox)",
        "BitTorrent tit-for-tat wording is not in week2; Huffman/ZIP remark (DEFLATE = LZ77 + Huffman) is textbook knowledge",
    ]:
        print("  -", s)
    sys.exit(1 if wrong else 0)
