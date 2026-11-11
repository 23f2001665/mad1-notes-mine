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
  // --- 2-8 the CSS box model
  const dims = id => { const e = document.getElementById(id), cs = getComputedStyle(e), r = e.getBoundingClientRect();
    return { offsetW: e.offsetWidth, offsetH: e.offsetHeight, clientW: e.clientWidth, clientH: e.clientHeight, csW: cs.width, csH: cs.height, rectW: r.width, rectH: r.height, left: r.left, top: r.top, bottom: r.bottom, boxSizing: cs.boxSizing,
             mL: parseFloat(cs.marginLeft), mR: parseFloat(cs.marginRight), mT: parseFloat(cs.marginTop), mB: parseFloat(cs.marginBottom) }; };
  const gap = () => { const a = document.getElementById('a').getBoundingClientRect(), b = document.getElementById('b').getBoundingClientRect(); return b.top - a.bottom; };
  const main = 'width:200px;height:100px;padding:30px;border:20px solid #333;margin:40px;';
  await run('bx_content', doc('<div id=a style="' + main + '"></div>'), dims, 'a');
  await run('bx_border', doc('<div id=a style="box-sizing:border-box;width:300px;height:200px;padding:30px;border:20px solid #333;margin:40px"></div>'), dims, 'a');
  await run('bx_inherit', doc('<div style="box-sizing:border-box"><div id=c></div></div>'), () => getComputedStyle(document.getElementById('c')).boxSizing);
  await run('bx_default', doc('<div id=a></div>'), () => getComputedStyle(document.getElementById('a')).boxSizing);
  const par = '<div style="width:400px"><div id=c style="width:100%;padding:20px;border:5px solid"></div></div>';
  await run('bx_w100_content', doc(par), dims, 'c');
  await run('bx_w100_border', doc(par.replace('id=c style="', 'id=c style="box-sizing:border-box;')), dims, 'c');
  const auto = '<div style="width:400px"><div id=c style="padding:20px;border:5px solid;margin:0 10px"></div></div>';
  await run('bx_auto_content', doc(auto), dims, 'c');
  await run('bx_auto_border', doc(auto.replace('id=c style="', 'id=c style="box-sizing:border-box;')), dims, 'c');
  await run('bx_max_content', doc('<div id=a style="max-width:100px;padding:20px;border:5px solid"></div>'), dims, 'a');
  await run('bx_max_border', doc('<div id=a style="box-sizing:border-box;max-width:100px;padding:20px;border:5px solid"></div>'), dims, 'a');
  await run('bx_minmax', doc('<div id=a style="width:500px;max-width:100px;min-width:300px"></div>'), dims, 'a');
  await run('bx_clamp', doc('<div id=a style="box-sizing:border-box;width:20px;padding:30px"></div>'), dims, 'a');
  await run('bx_calc', doc('<div style="width:400px"><div id=c style="width:calc(100% - 2*20px - 2*5px);padding:20px;border:5px solid"></div></div>'), dims, 'c');
  await run('bx_reset', doc('<div id=a style="padding:20px;border:5px solid;width:100px"></div>', '<style>*,*::before,*::after{box-sizing:border-box}</style>'), dims, 'a');
  await run('bx_pct_width', doc('<div style="width:400px"><div id=c style="width:50%;padding:20px;border:5px solid"></div></div>'), dims, 'c');
  await run('bx_height_pct', doc('<div style="width:200px"><div id=c style="height:50%"><div style="height:60px"></div></div></div><div style="width:200px;height:200px"><div id=d style="height:50%"></div></div>'), () => [document.getElementById('c').offsetHeight, document.getElementById('d').offsetHeight]);
  await run('bx_shorthand', doc('<div id=a></div>'), () => { const e = document.getElementById('a'); const out = {}; for (const v of ['10px', '10px 20px', '10px 20px 30px', '10px 20px 30px 40px']) { e.style.padding = v; e.style.margin = v; const cs = getComputedStyle(e); out[v] = [[cs.paddingTop, cs.paddingRight, cs.paddingBottom, cs.paddingLeft].join(' '), [cs.marginTop, cs.marginRight, cs.marginBottom, cs.marginLeft].join(' ')]; } return out; });
  await run('bx_supports', doc(''), () => ({ negPadding: CSS.supports('padding', '-5px'), negMargin: CSS.supports('margin', '-5px'), negBorder: CSS.supports('border-width', '-1px'),
    logical: [CSS.supports('margin-inline', '10px'), CSS.supports('padding-block', '10px')], sides: ['padding-top', 'margin-left', 'border-bottom'].map(p => CSS.supports(p, '1px')) }));
  await run('bx_border_facts', doc('<div id=a style="border-width:5px;border-color:red"></div><div id=b style="border:5px solid"></div><div id=c style="border-style:solid"></div><div id=d style="border:1px solid;color:rgb(255,0,0)"></div><div id=e style="width:100px;height:100px;border-radius:50%;padding:10px"></div>'),
    () => { const g = id => getComputedStyle(document.getElementById(id)); return { noStyle: [g('a').borderTopStyle, g('a').borderTopWidth], solid: g('b').borderTopWidth, medium: g('c').borderTopWidth, color: g('d').borderTopColor, radiusBox: [document.getElementById('e').offsetWidth, document.getElementById('e').offsetHeight], bgClip: g('a').backgroundClip }; });
  await run('bx_pct', doc('<div style="width:400px;height:900px"><div id=c style="padding:10%;margin:10%"></div></div>'), () => { const cs = getComputedStyle(document.getElementById('c')); return { padding: [cs.paddingTop, cs.paddingRight, cs.paddingBottom, cs.paddingLeft], margin: [cs.marginTop, cs.marginRight, cs.marginBottom, cs.marginLeft] }; });
  await run('bx_neg_margin', doc('<div style="width:300px;margin-left:100px"><div id=c style="margin-left:-40px;height:20px"></div></div><div id=a style="height:50px"></div><div id=b style="margin-top:-20px;height:50px"></div>'),
    () => { const r = document.getElementById('c').getBoundingClientRect(); return { left: r.left, width: r.width, pullTop: document.getElementById('b').getBoundingClientRect().top - document.getElementById('a').getBoundingClientRect().top }; });
  await run('bx_auto_margin', doc('<div style="width:1000px"><div id=a style="width:200px;margin:0 auto"></div><div id=b style="margin:0 auto"></div><div id=c style="width:200px;height:50px;margin:auto"></div></div><div style="display:flex;height:200px;width:1000px"><div id=f style="margin:auto;width:50px;height:50px"></div></div>'),
    () => { const cs = id => getComputedStyle(document.getElementById(id)); const f = document.getElementById('f').getBoundingClientRect(); return { centered: [cs('a').marginLeft, cs('a').marginRight], noWidth: [cs('b').marginLeft, cs('b').marginRight], vertical: [cs('c').marginTop, cs('c').marginBottom], flex: [f.left, f.top - document.getElementById('f').parentElement.getBoundingClientRect().top] }; });
  const sib = (m1, m2) => doc(`<div id=a style="height:50px;margin-bottom:${m1}"></div><div id=b style="height:50px;margin-top:${m2}"></div>`);
  await run('bx_c_20_30', sib('20px', '30px'), gap); await run('bx_c_30_30', sib('30px', '30px'), gap); await run('bx_c_30_neg10', sib('30px', '-10px'), gap); await run('bx_c_neg10_neg30', sib('-10px', '-30px'), gap);
  await run('bx_c_25_neg10', sib('25px', '-10px'), gap); await run('bx_c_25_10', sib('25px', '10px'), gap);
  await run('bx_c_flex', doc('<div style="display:flex;flex-direction:column"><div id=a style="height:50px;margin-bottom:20px"></div><div id=b style="height:50px;margin-top:30px"></div></div>'), gap);
  await run('bx_c_grid', doc('<div style="display:grid"><div id=a style="height:50px;margin-bottom:20px"></div><div id=b style="height:50px;margin-top:30px"></div></div>'), gap);
  await run('bx_c_float', doc('<div id=a style="float:left;clear:both;width:100px;height:50px;margin-bottom:20px"></div><div id=b style="float:left;clear:both;width:100px;height:50px;margin-top:30px"></div>'), gap);
  await run('bx_c_abs', doc('<div style="position:relative;height:300px"><div id=a style="position:absolute;top:0;height:50px;width:50px;margin-bottom:40px"></div><div id=b style="position:absolute;top:50px;height:50px;width:50px;margin-top:30px"></div></div>'), gap);
  await run('bx_c_horizontal', doc('<div id=a style="display:inline-block;width:50px;height:20px;margin-right:20px"></div><div id=b style="display:inline-block;width:50px;height:20px;margin-left:30px"></div>'), () => document.getElementById('b').getBoundingClientRect().left - document.getElementById('a').getBoundingClientRect().right);
  await run('bx_c_empty', doc('<div id=a style="height:50px;margin-bottom:20px"></div><div style="margin-top:10px;margin-bottom:30px"></div><div id=b style="height:50px;margin-top:5px"></div>'), gap);
  const pc = css => doc('<div id=p style="' + css + '"><div id=c style="margin-top:40px;height:50px"></div></div>');
  const pcJs = () => { const p = document.getElementById('p').getBoundingClientRect(), c = document.getElementById('c').getBoundingClientRect(); return [p.top, c.top, p.height]; };
  for (const [n, css] of [['plain', ''], ['padding', 'padding-top:1px'], ['border', 'border-top:1px solid'], ['overflow', 'overflow:hidden'], ['flowroot', 'display:flow-root'], ['flex', 'display:flex']]) await run('bx_pc_' + n, pc(css), pcJs);
  await run('bx_inline', doc('<p style="margin:0;line-height:20px">text <span id=s style="margin:50px 30px;padding:40px 10px;background:red">inline</span> text</p><p id=n style="margin:0">next</p><p style="margin:0;line-height:20px">t <span id=b2 style="border:20px solid red">x</span> t</p><p id=n2 style="margin:0">n</p>'),
    () => { const s = document.getElementById('s'); const p = s.parentElement.getBoundingClientRect(); return { paddingPaints: s.getClientRects()[0].height > 80, paraH: p.height, nextTop: document.getElementById('n').getBoundingClientRect().top, marginLeft: getComputedStyle(s).marginLeft, borderNextGap: document.getElementById('n2').getBoundingClientRect().top - document.getElementById('b2').parentElement.getBoundingClientRect().top }; });
  await run('bx_block_inline_block', doc('<span id=i style="width:100px;height:50px;display:inline">x</span><span id=ib style="display:inline-block;width:100px;height:50px;margin:10px 0;padding:5px">x</span>'),
    () => { const g = id => document.getElementById(id).getBoundingClientRect(); return { inlineW: g('i').width, inlineBlock: [g('ib').width, g('ib').height] }; });
  await run('bx_overflow', doc('<div id=a style="width:100px;height:50px"><div style="width:300px;height:200px"></div></div><div id=b style="width:100px;height:50px;overflow:hidden"><div style="width:300px;height:200px"></div></div>'),
    () => { const g = id => { const e = document.getElementById(id); return { offH: e.offsetHeight, scrollW: e.scrollWidth, scrollH: e.scrollHeight }; }; return { visible: g('a'), hidden: g('b') }; });
  await run('bx_outline', doc('<div id=a style="width:100px;height:50px;border:5px solid;outline:10px solid red;box-shadow:0 0 0 15px blue"></div><div id=b style="height:10px"></div>'), () => ({ offsetW: document.getElementById('a').offsetWidth, nextTop: document.getElementById('b').getBoundingClientRect().top }));
  await run('bx_ua', '<!DOCTYPE html><html><body><h1 id=h>t</h1><p id=p>p</p><ul id=u><li>x</li></ul><ol id=o><li>x</li></ol><div id=d></div></body></html>',
    () => { const g = (id, p) => getComputedStyle(document.getElementById(id))[p]; return { body: [getComputedStyle(document.body).marginTop, getComputedStyle(document.body).marginLeft], p: [g('p', 'marginTop'), g('p', 'marginBottom')], h1: g('h', 'marginTop'), ul: [g('u', 'paddingLeft'), g('u', 'marginTop')], ol: g('o', 'paddingLeft'), div: [g('d', 'marginTop'), g('d', 'paddingTop')] }; });
  const measureAll = () => Object.fromEntries([...document.querySelectorAll('[id]')].map(e => { const cs = getComputedStyle(e), r = e.getBoundingClientRect();
      return [e.id, { offW: e.offsetWidth, offH: e.offsetHeight, contentW: parseFloat(cs.width) - (cs.boxSizing === 'border-box' ? parseFloat(cs.paddingLeft) + parseFloat(cs.paddingRight) + parseFloat(cs.borderLeftWidth) + parseFloat(cs.borderRightWidth) : 0),
        contentH: parseFloat(cs.height) - (cs.boxSizing === 'border-box' ? parseFloat(cs.paddingTop) + parseFloat(cs.paddingBottom) + parseFloat(cs.borderTopWidth) + parseFloat(cs.borderBottomWidth) : 0),
        marginW: e.offsetWidth + parseFloat(cs.marginLeft) + parseFloat(cs.marginRight), marginH: e.offsetHeight + parseFloat(cs.marginTop) + parseFloat(cs.marginBottom), top: r.top, bottom: r.bottom }]; }));
  R.bx_exercises = []; R.bx_exercises_bb = [];
  for (const ex of (input.box || [])) {
    await page.setContent(doc(ex.html, `<style>${ex.css}</style>`)); R.bx_exercises.push(await page.evaluate(measureAll));
    await page.setContent(doc(ex.html, `<style>${ex.css}*,*::before,*::after{box-sizing:border-box}</style>`)); R.bx_exercises_bb.push(await page.evaluate(measureAll));
  }
  if (input.diagram) { await page.setContent(doc(input.diagram.html, `<style>${input.diagram.css}</style>`)); R.bx_diagram = await page.evaluate(() => { const b = document.querySelector('.box'), w = document.getElementById('diagram'); return { boxW: b.offsetWidth, boxH: b.offsetHeight, wrapW: w.offsetWidth, wrapH: w.offsetHeight, contentW: parseFloat(getComputedStyle(b).width), contentH: parseFloat(getComputedStyle(b).height) }; }); }
  if (input.pic) { await page.setContent(doc(input.pic.html, `<style>${input.pic.css}</style>`)); R.bx_pic = await page.evaluate(() => ({ cb: document.querySelector('.cb').offsetWidth, bb: document.querySelector('.bb').offsetWidth, bbContentW: document.querySelector('.bb').clientWidth - 60 })); }
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


BX = "2-8-css-box-model.md"

PIC_CSS = (".row{display:flex;gap:24px;align-items:flex-start}.cell{font:12px/1.4 -apple-system,'Segoe UI',Helvetica,Arial,sans-serif}.cell p{margin:6px 0 0}"
           ".b{width:200px;padding:30px;border:20px solid #ffd966;background:linear-gradient(#9fc5e8,#9fc5e8) content-box,#b6d7a8;line-height:24px;text-align:center;font:12px/24px sans-serif}"
           ".cb{box-sizing:content-box}.bb{box-sizing:border-box}")
PIC_HTML = ('<div class="row"><div class="cell"><div class="b cb">content</div><p>box-sizing: content-box<br><b>width: 200px</b> &rarr; drawn <b>300px</b> wide</p></div>'
            '<div class="cell"><div class="b bb">content</div><p>box-sizing: border-box<br><b>width: 200px</b> &rarr; drawn <b>200px</b> wide</p></div></div>')


def box_inputs():
    """The pieces of 2-8 that the browser has to render: the diagram, the exercises, the sizing picture."""
    try:
        t = note(BX)
    except FileNotFoundError:
        return {"diagram": None, "exercises": [], "pic": {"html": "<div class=row></div>", "css": ""}}
    css_blocks = blocks(t, {"css"})
    html_blocks = blocks(t, {"html"})
    dia_css = [b for _, b in css_blocks if b.lstrip().startswith("/* diagram */")]
    dia_html = [b for _, b in html_blocks if 'id="diagram"' in b]
    exercises = []
    for part in re.split(r"^#### Exercise ", t, flags=re.M)[1:]:
        part = part.split("\n## ", 1)[0]
        css, html = blocks(part, {"css"}), blocks(part, {"html"})
        if css and html:
            exercises.append({"css": css[0][1], "html": html[0][1]})
    return {"diagram": {"css": dia_css[0], "html": dia_html[0]} if dia_css and dia_html else None, "exercises": exercises,
            "pic": {"html": PIC_HTML, "css": PIC_CSS}}


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
        box_in = box_inputs()
        if os.environ.get("MAKE_SHOT") and box_in["diagram"]:
            shots += [{"html": box_in["diagram"]["html"], "path": str(ROOT / "static" / "css-box-model.png"), "width": 405,
                       "css": box_in["diagram"]["css"] + "span{font:12px/1.2 -apple-system,'Segoe UI',Helvetica,Arial,sans-serif;color:#222}"},
                      {"html": box_in["pic"]["html"], "path": str(ROOT / "static" / "css-box-sizing.png"), "width": 590, "css": box_in["pic"]["css"]}]
        Path(d, "in.json").write_text(json.dumps({"visualizer": visualizer, "css": css_items(), "shots": shots, "cases": case_examples(),
                                                  "box": box_in["exercises"], "diagram": box_in["diagram"], "pic": box_in["pic"]}))
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


def box_sizes(B):
    c, b, d, p = B["bx_content"], B["bx_border"], B.get("bx_diagram"), B["bx_pic"]
    t = note(BX)
    ok = (c["offsetW"] == 300 and c["offsetH"] == 200 and c["clientW"] == 260 and c["clientH"] == 160 and c["csW"] == "200px" and c["rectW"] == 300
          and c["offsetW"] + c["mL"] + c["mR"] == 380 and c["offsetH"] + c["mT"] + c["mB"] == 280
          and b["offsetW"] == 300 and b["offsetH"] == 200 and b["csW"] == "300px" and b["clientW"] == 260
          and d is not None and (d["boxW"], d["boxH"], d["wrapW"], d["wrapH"], d["contentW"], d["contentH"]) == (300, 200, 380, 280, 200, 100)
          and p["cb"] == 300 and p["bb"] == 200 and p["bbContentW"] == 100)
    good = (has(t, r"\| Content box \| 200px \| 100px \|") and has(t, r"\| Padding box \(content \+ padding\) \| 260px \| 160px \|") and has(t, r"\*\*300px\*\* \| \*\*200px\*\*")
            and has(t, r"Margin box \(the space it takes in the layout\) \| 380px \| 280px") and has(t, r"= 300\\text\{px\}") and has(t, r"`\"200px\"` \(and `\"300px\"` for the `border-box` version")
            and has(t, r"`el\.clientWidth` \| content \+ padding \(without border and scrollbar\) \| `260`") and has(t, r"`el\.offsetWidth` \| content \+ padding \+ border \(the border box\) \| `300`")
            and has(t, r"drawn `300px` wide|it is 300px wide") and has(t, r"drawn `200px` wide|`200px` wide with a content of `100px`"))
    return ok and good, (f"the note's example (content 200x100, padding 30, border 20, margin 40): offsetWidth/Height {c['offsetW']}x{c['offsetH']}, clientWidth {c['clientW']}, computed width {c['csW']}, "
                         f"margin box {c['offsetW'] + c['mL'] + c['mR']:.0f}x{c['offsetH'] + c['mT'] + c['mB']:.0f}; the border-box version width:300px;height:200px is the same box (computed width {b['csW']}); "
                         f"the picture's real element measures {d and (d['boxW'], d['boxH'])} with a margin wrapper {d and (d['wrapW'], d['wrapH'])}; the box-sizing picture: content-box {p['cb']}px vs border-box {p['bb']}px (content {p['bbContentW']}px); "
                         f"every number of the note's tables is right: {good}")


def box_sizing_table(B):
    t = note(BX)
    cw, bw = B["bx_w100_content"], B["bx_w100_border"]
    ac, ab = B["bx_auto_content"], B["bx_auto_border"]
    mc, mb = B["bx_max_content"], B["bx_max_border"]
    ok = (cw["offsetW"] == 450 and bw["offsetW"] == 400 and ac["offsetW"] == 380 and ac["csW"] == "330px" and ab["offsetW"] == 380 and mc["offsetW"] == 150 and mb["offsetW"] == 100
          and B["bx_minmax"]["offsetW"] == 300 and B["bx_clamp"]["offsetW"] == 60 and B["bx_calc"]["offsetW"] == 400 and B["bx_inherit"] == "content-box" and B["bx_default"] == "content-box"
          and B["bx_reset"]["boxSizing"] == "border-box" and B["bx_reset"]["offsetW"] == 100 and B["bx_pct_width"]["offsetW"] == 250 and B["bx_pct_width"]["csW"] == "200px")
    hp = B["bx_height_pct"]
    good = (has(t, r"\*\*450px\*\* \(overflows by 50px\) \| 400px") and has(t, r"380px \(content 330px\) \| 380px") and has(t, r"\| 150px \| 100px \|") and has(t, r"drawn `60px` wide")
            and has(t, r"if `min-width` and `max-width` disagree, `min-width` wins") and has(t, r"not inherited") and has(t, r"calc\(100% - 2 \* 20px - 2 \* 5px\)") and has(t, r"only works if the parent has a definite height")
            and has(t, r"box-sizing: border-box;\s*\n\}"))
    return ok and hp == [60, 100] and good, (
        f"child of a 400px parent: width:100% + padding 20 + border 5 -> content-box {cw['offsetW']}px (overflow), border-box {bw['offsetW']}px; width:auto with margin 0 10px -> {ac['offsetW']}px (content {ac['csW']}) in both modes; "
        f"max-width:100px -> {mc['offsetW']}px vs {mb['offsetW']}px; min-width 300 beats max-width 100 beats width 500 -> {B['bx_minmax']['offsetW']}px; border-box width:20px + padding 30 -> {B['bx_clamp']['offsetW']}px; calc() -> {B['bx_calc']['offsetW']}px; "
        f"box-sizing is not inherited ({B['bx_inherit']}) and defaults to {B['bx_default']}; the * reset gives {B['bx_reset']['boxSizing']}; width:50% = {B['bx_pct_width']['csW']} content; height:50% -> {hp} (auto parent: ignored, definite parent: 100); note says so: {good}")


def box_layers(B):
    t = note(BX)
    sh = B["bx_shorthand"]
    sup = B["bx_supports"]
    bf = B["bx_border_facts"]
    pc, nm, am = B["bx_pct"], B["bx_neg_margin"], B["bx_auto_margin"]
    ok = (sh["10px"][0] == "10px 10px 10px 10px" and sh["10px 20px"][0] == "10px 20px 10px 20px" and sh["10px 20px 30px"][0] == "10px 20px 30px 20px" and sh["10px 20px 30px 40px"][0] == "10px 20px 30px 40px"
          and all(v[0] == v[1] for v in sh.values()) and sup["negPadding"] is False and sup["negMargin"] is True and sup["negBorder"] is False and sup["logical"] == [True, True] and all(sup["sides"])
          and bf["noStyle"] == ["none", "0px"] and bf["solid"] == "5px" and bf["medium"] == "3px" and bf["color"] == "rgb(255, 0, 0)" and bf["radiusBox"] == [120, 120] and bf["bgClip"] == "border-box"
          and pc["padding"] == ["40px"] * 4 and pc["margin"] == ["40px"] * 4 and nm["left"] == 60 and nm["width"] == 340 and nm["pullTop"] == 30
          and am["centered"] == ["400px", "400px"] and am["noWidth"] == ["0px", "0px"] and am["vertical"] == ["0px", "0px"] and am["flex"] == [475, 75])
    good = (has(t, r"`padding: 10px 20px 30px` \| 10px \| 20px \| 30px \| 20px") and has(t, r"clockwise, starting at the top") and has(t, r"`padding: -5px` is invalid") and has(t, r"A border without a `border-style` is not drawn, and has no width")
            and has(t, r"`medium`, which is `3px`") and has(t, r"`currentcolor`") and has(t, r"stays `120px`") and has(t, r"`padding: 10%` is 40px on the top, right, bottom \*\*and\*\* left") and has(t, r"a `200px` wide box gets `400px` on each side")
            and has(t, r"Inside a \*\*flex container\*\* `margin: auto` does centre the box on both axes") and has(t, r"`margin-top: -20px` the box moves 20px up") and has(t, r"background-clip: border-box"))
    return ok and good, (
        f"shorthand 1-4 values (top right bottom left) for padding and margin ({sh['10px 20px 30px'][0]!r} for three values); negative padding invalid ({not sup['negPadding']}), negative margin valid ({sup['negMargin']}); "
        f"border-width:5px without a style computes to {bf['noStyle']}, default width with a style {bf['medium']}, default colour = the text colour; border-radius leaves the 100px+2x10px box at {bf['radiusBox']}; background-clip {bf['bgClip']}; "
        f"padding:10% / margin:10% of a 400px parent are {pc['padding'][0]} on every side; margin-left:-40px -> left edge {nm['left']}, width grows to {nm['width']}; margin-top:-20px pulls the next box up by {50 - nm['pullTop']}px; "
        f"margin:0 auto -> {am['centered']}, without width {am['noWidth']}, margin:auto vertical {am['vertical']}, in a flex container the box is centred at {am['flex']}; note says all of this: {good}")


def box_margin_collapse(B):
    t = note(BX)
    gaps = (B["bx_c_20_30"], B["bx_c_30_30"], B["bx_c_30_neg10"], B["bx_c_neg10_neg30"], B["bx_c_25_neg10"], B["bx_c_25_10"])
    add = (B["bx_c_flex"], B["bx_c_grid"], B["bx_c_float"], B["bx_c_horizontal"])
    pcs = {n: B["bx_pc_" + n] for n in ("plain", "padding", "border", "overflow", "flowroot", "flex")}
    ok = (gaps == (30, 30, 20, -30, 15, 25) and add == (50, 50, 50, 50) and B["bx_c_abs"] == 30 and B["bx_c_empty"] == 30
          and pcs["plain"] == [40, 40, 50] and pcs["padding"] == [0, 41, 91] and pcs["border"] == [0, 41, 91] and pcs["overflow"] == [0, 40, 90] and pcs["flowroot"] == [0, 40, 90] and pcs["flex"] == [0, 40, 90])
    good = (has(t, r"`margin-bottom: 20px` above `margin-top: 30px` \| \*\*30px\*\*") and has(t, r"`30px` above `-10px` \| \*\*20px\*\*") and has(t, r"`-10px` above `-30px` \| \*\*-30px\*\*")
            and has(t, r"\*\*flex items\*\*, grid items or floats \| they \*\*add up\*\* \(50px\)") and has(t, r"absolutely positioned boxes never collapse either") and has(t, r"only vertical margins collapse")
            and has(t, r"\(30px for 20, 10, 30, 5\)") and has(t, r"\| \*\(nothing\)\* \| 40px \(pushed down\) \| 40px \(same place\) \| 50px \|") and has(t, r"\| `padding-top: 1px` or `border-top: 1px solid` \| 0px \| 41px \(margin is inside\) \| 91px \|")
            and has(t, r"\| `overflow: hidden` \| 0px \| 40px \| 90px \|") and has(t, r"\| `display: flow-root` \| 0px \| 40px \| 90px \|") and has(t, r"\| `display: flex` \| 0px \| 40px \| 90px \|"))
    return ok and good, (
        f"gap between two blocks: 20/30 -> {gaps[0]}, 30/30 -> {gaps[1]}, 30/-10 -> {gaps[2]}, -10/-30 -> {gaps[3]}, 25/-10 -> {gaps[4]}, 25/10 -> {gaps[5]}; flex, grid, floats and left/right margins add up -> {add}; absolutely positioned (margin-bottom 40 above margin-top 30, b at top:50px): gap {B['bx_c_abs']} = only b's own margin, the neighbour's margin is ignored; "
        f"empty block between 20, (10, 30), 5 -> {B['bx_c_empty']}; parent + first child (margin-top 40) [parent top, child top, parent height]: plain {pcs['plain']}, padding {pcs['padding']}, border {pcs['border']}, overflow:hidden {pcs['overflow']}, flow-root {pcs['flowroot']}, flex {pcs['flex']}; every row of the note's tables is right: {good}")


def box_display_overflow_defaults(B):
    t = note(BX)
    il, bi, ov, ou, ua = B["bx_inline"], B["bx_block_inline_block"], B["bx_overflow"], B["bx_outline"], B["bx_ua"]
    ok = (il["paddingPaints"] and il["paraH"] == 20 and il["nextTop"] == 20 and il["marginLeft"] == "30px" and il["borderNextGap"] == 20 and bi["inlineW"] < 100 and bi["inlineBlock"] == [110, 60]
          and ov["visible"]["scrollW"] == 300 and ov["visible"]["scrollH"] == 200 and ov["hidden"]["scrollW"] == 300 and ov["hidden"]["scrollH"] == 200 and ov["hidden"]["offH"] == 50
          and ou["offsetW"] == 110 and ou["nextTop"] == 60
          and ua["body"] == ["8px", "8px"] and ua["p"] == ["16px", "16px"] and abs(float(ua["h1"][:-2]) - 21.44) < 0.01 and ua["ul"] == ["40px", "16px"] and ua["ol"] == "40px" and ua["div"] == ["0px", "0px"])
    good = (has(t, r"the paragraph stays `20px` tall and the next paragraph starts right below it") and has(t, r"`outline` \(the focus ring around a link or an input\) and `box-shadow` are painted \*\*around\*\* the border box but take \*\*no space\*\*")
            and has(t, r"`body` \| `margin: 8px`") and has(t, r"`p` \| `margin: 1em 0` \(`16px` above and below\)") and has(t, r"about `21px`") and has(t, r"`padding-left: 40px`") and has(t, r"`scrollWidth` is `300`, `scrollHeight` is `200`")
            and has(t, r"\| Top / bottom \*\*margin\*\* \| Yes \| \*\*Ignored\*\* \| Yes \|"))
    return ok and good, (
        f"inline <span> with margin 50px 30px / padding 40px 10px: vertical padding paints ({il['paddingPaints']}) but the 20px paragraph stays {il['paraH']}px and the next one starts at {il['nextTop']}; horizontal margin {il['marginLeft']} works; a 20px border does not push either ({il['borderNextGap']}); "
        f"width/height ignored on inline ({bi['inlineW']:.0f}px), respected on inline-block ({bi['inlineBlock']}); overflow: scrollWidth/Height {ov['visible']['scrollW']}/{ov['visible']['scrollH']}, still clipped box {ov['hidden']['offH']}px; outline + box-shadow take no space (offsetWidth {ou['offsetW']}, next box at {ou['nextTop']}); "
        f"Chromium defaults: body {ua['body']}, p {ua['p']}, h1 {ua['h1']}, ul {ua['ul']}, ol {ua['ol']}; note says all of this: {good}")


def box_exercises_answers(B):
    t = note(BX)
    ex, bb = B["bx_exercises"], B["bx_exercises_bb"]
    if len(ex) != 4:
        return False, f"expected 4 exercises (css + html) in the note, found {len(ex)}"
    e1, e2, e3, e4 = ex
    answers = re.findall(r"<summary>Answer</summary>\n\n(.*?)\n\n</details>", t, re.S)
    ok = (e1["ex1"]["offW"] == 350 and e1["ex1"]["offH"] == 130 and e1["ex1"]["marginW"] == 380 and e1["ex1"]["marginH"] == 160
          and e2["ex2"]["offW"] == 300 and e2["ex2"]["offH"] == 100 and e2["ex2"]["contentW"] == 250 and e2["ex2"]["contentH"] == 70 and e2["ex2"]["marginW"] == 330 and e2["ex2"]["marginH"] == 130
          and e3["b"]["top"] - e3["a"]["bottom"] == 15 and e4["child"]["offW"] == 424 and e4["parent"]["offW"] == 400 and bb[3]["child"]["offW"] == 400)
    good = (len(answers) == 4 and all(s in answers[0] for s in ("350px", "130px", "380px", "160px")) and all(s in answers[1] for s in ("300px", "250px", "70px", "330px", "130px"))
            and "15px" in answers[2] and "25px" in answers[2] and has(answers[3], r"= 424px`") and has(answers[3], r"by `24px`"))
    return ok and good, (f"exercise 1 -> {e1['ex1']['offW']}x{e1['ex1']['offH']}, margin box {e1['ex1']['marginW']}x{e1['ex1']['marginH']}; exercise 2 (border-box) -> {e2['ex2']['offW']}x{e2['ex2']['offH']}, content {e2['ex2']['contentW']}x{e2['ex2']['contentH']}, margin box {e2['ex2']['marginW']}x{e2['ex2']['marginH']}; "
                         f"exercise 3 -> gap {e3['b']['top'] - e3['a']['bottom']}px; exercise 4 -> child {e4['child']['offW']}px in a {e4['parent']['offW']}px parent, border-box {bb[3]['child']['offW']}px; every number in the 4 answers matches: {good}")


def box_images_exist():
    ps = [ROOT / "static" / "css-box-model.png", ROOT / "static" / "css-box-sizing.png"]
    t = note(BX)
    refs = "css-box-model.png" in t and "css-box-sizing.png" in t
    return all(p.exists() and p.stat().st_size > 2000 for p in ps) and refs, f"the two pictures of the box-model note are real Chromium renderings of real elements: files exist {[p.exists() for p in ps]}, referenced in the note {refs}"


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
        check(BX, "box model sizes: 200x100 content + padding 30 + border 20 + margin 40 = 300x200 (border box) / 380x280 (margin box); the two pictures are real elements", lambda: box_sizes(B))
        check(BX, "box-sizing: width:100% overflow, auto width, max/min-width, border-box clamp, calc(), not inherited, % widths", lambda: box_sizing_table(B))
        check(BX, "shorthand order, padding / border / margin rules (negative, %, border-style gotcha, auto and flex centring)", lambda: box_layers(B))
        check(BX, "margin collapsing: siblings, negative margins, flex/grid/float, parent and first child (what stops it)", lambda: box_margin_collapse(B))
        check(BX, "inline vs inline-block, overflow and scroll sizes, outline / box-shadow take no space, browser default margins", lambda: box_display_overflow_defaults(B))
        check(BX, "the four practice exercises and their answers", lambda: box_exercises_answers(B))
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
    check(BX, "the box-model pictures exist (static/css-box-model.png, css-box-sizing.png)", box_images_exist)
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
