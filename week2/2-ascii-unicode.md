
# Representing Text 

::: tip Representing Text on computers
Computers ultimately work with **bits** (0 and 1). So we need some Standard “encoding” i.e. **some sequence of bits represent a specific character**
:::


## ASCII

::: tip American Standard Code for **Information Interchange**: is a character encoding used by machines to represent text → assigns a unique numerical value to each character. 
$$\begin{gather}\text{ASCII uses 7-bits, allowing $2^7 = 128$ unique characters} \\ \text{i.e. digits + uppercase and lowercase English alphabets + control symbols}\\\underbrace{0...9}_{48 -57}+\underbrace{A...Z}_{65 -90}+ \underbrace{a...z}_{97-122}
\end{gather}$$
<img style="margin: auto;" src="https://blog.gcwizard.net/wp-content/uploads/2021/01/ASCII-code.png">

But if we want to include `!@# %&*() -Ľätīń/Rõman` symbols, we can use **extended 8-bit encodings**, allowing up to $2^8 =256$ characters! (not global standard)


- `"A"` in binary is `01000001`=$2^6+2^0=64+1=65$ 
- `"a"` in binary is `01100001`=$2^6+ 2^5 + 2^0= 64+32+1=97$
- The difference between uppercase and lowercase letters in ASCII is a single bit. <br>the 5th bit (counting from the right, starting at 0) differs. `Uppercase have this bit = 0, lowercase have this bit =1`

:::

ASCII works well for English✅ but the world has many languages अ (Hindi), அ (Tamil), 不 (Chinese)
cannot be represented in 7-bit ASCII⚠️

## Unicode
Unicode is a `universal character standard` that assigns a unique number (code point) to every character, across:
- All major languages
- Symbols, emojis, math, arrows etc.
Characters are written as `code points`:
$$\text{U+XXXX (hexadecimal)}$$

&emsp;&emsp;&emsp;&emsp;&emsp; 'a' → `U+0061` &emsp;&emsp;&emsp;&emsp;&emsp; 'अ' → `U+0905` &emsp;&emsp;&emsp;&emsp; 😀 → `U+1F600`

::: details Unicode Code Space (UCS)

UCS defines the range of code points; encodings define how they are stored in memory.
| Encoding           | Bytes per character | Max characters               |
| ------------------ | ------------------- | ---------------------------- |
| **UCS-2**          | 2 bytes             | $2^{16}=65,536$            |
| **UCS-4 / UTF-32** | 4 bytes             | $2^{32} \approx \text{ 4.3 billion}$ |
:::

:::details Problem 1.❓ A text document contains:<br>**1000 words**<br>Approximately **5000 characters** (including spaces)<br>How much bits will be required to store it in `UCS-4, 8 bit ASCII, 7 bit ASCII, 6 bits`?

| Encoding Scheme           | Bits per Character | Total Bits Required               |
| ------------------------- | ------------------ | --------------------------------- |
| UCS-4                     | 32 bits            | $32 \times 5000 = 160{,}000$ bits |
| ASCII (8-bit)             | 8 bits             | $8 \times 5000 = 40{,}000$ bits   |
| Original ASCII            | 7 bits             | $7 \times 5000 = 35{,}000$ bits   |
| Minimal alphabet encoding | ~6 bits            | $6 \times 5000 = 30{,}000$ bits   |

- Assigning fewer bits to more frequent characters (e, t, a, o) is the idea behind [Huffman coding](https://engineering.purdue.edu/ece264/17au/hw/HW13?alt=huffman).<br>
ZIP files use such compression techniques to store data efficiently.
:::


### Why UTF-8 is the most successful Unicode encoding?
UTF-8 is a variable-length encoding used to store Unicode characters efficiently.

✅ Backward compatible with ASCII<br>
✅ Efficient for English text<br>
✅ Can encode all Unicode characters<br>
✅ Most common encoding on the Web 🌐
<iframe
  width="100%"
  height="400"
  src="https://www.youtube.com/embed/MijmeoH9LT4"
  title="YouTube video player"
  frameborder="0"
  allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share"
  allowfullscreen>
</iframe>

- ⚠️UCS-4 uses 4 bytes per character so even simple character 'A' wastes `32 bits`
  - ✅Use short encodings for common characters (1 byte for alphabets)
  - ✅Use longer encodings for rare characters

::: details Prefix coding rules apply **only to UTF-8**.

Decoder must:
- Read the **1st byte prefix**, which tells how many bytes follow.
- Read remaining bytes

| Bytes Used | 1st Byte Pattern | 2nd Byte | 3rd Byte | 4th Byte | Unicode Range |
|-----------|------------------|----------|----------|----------|---------------|
| 1 byte | 0xxxxxxx | — | — | — | U+0000 – U+007F (127) |
| 2 bytes | 110xxxxx | 10xxxxxx | — | — | U+0080 – U+07FF (2,047) |
| 3 bytes | 1110xxxx | 10xxxxxx | 10xxxxxx | — | U+0800 – U+FFFF (65,535) |
| 4 bytes | 11110xxx | 10xxxxxx | 10xxxxxx | 10xxxxxx | U+10000 – U+10FFFF (1,114,111) |

- **UTF-8** is a variable-length, prefix-based encoding (1 to 4 bytes).
- **UTF-16** uses 2 or 4 bytes (via surrogate pairs), but does NOT use prefix bits.
- **UTF-32** always uses exactly 4 bytes and has no prefix rules.

:::


## Markup

Markup is a way of adding special cues or codes within normal text to control how the text is structured or displayed, making it *clearer and easier to understand*.
<div class="card">
  <h3>
    1. Presentational Markup
  </h3>
  <ul>
    <li>Focuses on <strong>how text looks</strong></li>
    <li>Formatting codes are <em>specific to the editor</em>, not part of regular text</li>
    <li>Does <strong>not</strong> describe the meaning of content</li>
    <li>✅ <strong>WYSIWYG</strong> (What You See Is What You Get) → direct visual editing</li>
    <li><strong>Examples:</strong> MS Word, Google Docs</li>
  </ul>
</div>

<div class="card">
  <h3>
    2. Procedural Markup
  </h3>
  <ul>
    <li>Describes <strong>steps or procedures</strong> to format text</li>
    <li>Example instructions:</li>
    <ul>
      <li>1️⃣ Change font → make it large and bold</li>
      <li>2️⃣ Indent by two lines</li>
    </ul>
    <li>Emphasizes <strong>how to format</strong>, not what the content means</li>
  </ul>
</div>

<div class="card">
  <h3>
    3. Descriptive Markup
  </h3>
  <ul>
    <li>Describes the <strong>meaning and structure</strong> of content</li>
    <li>Actual appearance is decided by the <strong>renderer</strong> (browser / compiler)</li>
    <li>✅ Clear semantic meaning</li>
    <li>❌ Not WYSIWYG while writing</li>
    <li>
      Example structure:
      <code>&lt;title&gt; with &lt;heading&gt; within 2 &lt;paragraph&gt;s</code>
    </li>
    <li><strong>Examples:</strong> LaTeX, HTML</li>
  </ul>
</div>
