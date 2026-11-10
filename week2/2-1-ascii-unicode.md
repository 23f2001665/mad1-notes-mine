
# Representing Text 

> [!TIP]
> **Representing Text on computers**
>
> Computers ultimately work with **bits** (0 and 1). So we need some Standard “encoding” i.e. **some sequence of bits represent a specific character**


## ASCII

> [!TIP]
> **American Standard Code for Information Interchange (ASCII)** is a character encoding used by machines to represent text → assigns a unique numerical value to each character.

$$\begin{gather}\text{ASCII uses 7 bits, allowing } 2^7 = 128 \text{ unique characters} \\ \text{i.e. digits + uppercase and lowercase English alphabets + punctuation + control characters}
\\
\underbrace{0...9}_{48 -57}+\underbrace{A...Z}_{65 -90}+ \underbrace{a...z}_{97-122}
\end{gather}$$

![ASCII table](https://blog.gcwizard.net/wp-content/uploads/2021/01/ASCII-code.png)

Punctuation such as `!@#%&*()-/` is already part of ASCII. But if we want letters like `é ü ñ £ ©`, we can use **extended 8-bit encodings** (for example ISO 8859-1, "Latin-1"), allowing up to $2^8 =256$ characters! (not a global standard: codes 128–255 mean different characters in different extended encodings, e.g. `Ľ` exists in Latin-2 but not in Latin-1)


- `"A"` in binary is `01000001`= $2^6+2^0=64+1=65$ 
- `"a"` in binary is `01100001`= $2^6+ 2^5 + 2^0= 64+32+1=97$
- The difference between uppercase and lowercase letters in ASCII is a single bit (value $2^5 = 32$, that is why `'a' - 'A' = 32`). <br>the 5th bit (counting from the right, starting at 0) differs. `Uppercase have this bit = 0, lowercase have this bit =1`

ASCII works well for English✅ but the world has many languages अ (Hindi), அ (Tamil), 不 (Chinese)
cannot be represented in 7-bit ASCII⚠️

## Unicode
Unicode is a `universal character standard` that assigns a unique number (code point) to every character, across:
- All major languages
- Symbols, emojis, math, arrows etc.
Characters are written as `code points`:
$$\text{U+XXXX (hexadecimal)}$$

| Character | Code point |
| --- | --- |
| 'a' | `U+0061` |
| 'अ' | `U+0905` |
| 😀 | `U+1F600` |

<details>
<summary>Unicode Code Space (UCS)</summary>

UCS defines the range of code points; encodings define how they are stored in memory.

| Encoding           | Bytes per character | Max characters               |
| ------------------ | ------------------- | ---------------------------- |
| **UCS-2**          | 2 bytes             | $2^{16}=65,536$            |
| **UCS-4 / UTF-32** | 4 bytes             | $2^{32} \approx \text{ 4.3 billion}$ |

Unicode itself only defines code points from `U+0000` to `U+10FFFF`, i.e. 1,114,112 code points, so most of the $2^{32}$ values of UCS-4 / UTF-32 are never used. (UCS-2 can only reach `U+FFFF`; UTF-16 extends it with surrogate pairs.)

</details>

**❓ Problem 1.** A text document contains:<br>**1000 words**<br>Approximately **5000 characters** (including spaces)<br>How many bits will be required to store it in `UCS-4, 8 bit ASCII, 7 bit ASCII, 6 bits`?

<details>
<summary>Show solution</summary>

| Encoding Scheme           | Bits per Character | Total Bits Required               |
| ------------------------- | ------------------ | --------------------------------- |
| UCS-4                     | 32 bits            | $32 \times 5000 = 160{,}000$ bits |
| ASCII (8-bit)             | 8 bits             | $8 \times 5000 = 40{,}000$ bits   |
| Original ASCII            | 7 bits             | $7 \times 5000 = 35{,}000$ bits   |
| Minimal alphabet encoding | ~6 bits            | $6 \times 5000 = 30{,}000$ bits   |

- Assigning fewer bits to more frequent characters (e, t, a, o) is the idea behind [Huffman coding](https://engineering.purdue.edu/ece264/17au/hw/HW13?alt=huffman).<br>
ZIP files use such compression techniques to store data efficiently.

</details>


### Why UTF-8 is the most successful Unicode encoding?
UTF-8 is a variable-length encoding used to store Unicode characters efficiently.

✅ Backward compatible with ASCII<br>
✅ Efficient for English text<br>
✅ Can encode all Unicode characters<br>
✅ Most common encoding on the Web 🌐

[A small youtube video on UTF-8](https://www.youtube.com/watch?v=MijmeoH9LT4)


- ⚠️UCS-4 uses 4 bytes per character so even a simple character like 'A' takes `32 bits` although 7 are enough (25 bits are wasted)
  - ✅Use short encodings for common characters (1 byte for alphabets)
  - ✅Use longer encodings for rare characters

<details>
<summary>Prefix coding rules (UTF-8 uses them, UTF-16 and UTF-32 do not)</summary>

Decoder must:
- Read the **1st byte prefix**, which tells how many bytes follow.
- Read remaining bytes

| Bytes Used | 1st Byte Pattern | 2nd Byte | 3rd Byte | 4th Byte | Unicode Range |
|-----------|------------------|----------|----------|----------|---------------|
| 1 byte | 0xxxxxxx | — | — | — | U+0000 – U+007F (127) |
| 2 bytes | 110xxxxx | 10xxxxxx | — | — | U+0080 – U+07FF (2,047) |
| 3 bytes | 1110xxxx | 10xxxxxx | 10xxxxxx | — | U+0800 – U+FFFF (65,535) |
| 4 bytes | 11110xxx | 10xxxxxx | 10xxxxxx | 10xxxxxx | U+10000 – U+10FFFF (1,114,111) |

The values `U+D800` – `U+DFFF` (surrogates) are not characters and are never encoded in UTF-8.

- **UTF-8** is a variable-length, prefix-based encoding (1 to 4 bytes).
- **UTF-16** uses 2 or 4 bytes. The 4-byte form is a surrogate pair: two reserved 2-byte values (`U+D800` – `U+DFFF`) that together stand for one character. It has no UTF-8 style prefix bytes.
- **UTF-32** always uses exactly 4 bytes and has no prefix rules.

</details>


## Markup

Markup is a way of adding special cues or codes within normal text to control how the text is structured or displayed, making it *clearer and easier to understand*.

### 1. Presentational Markup

- Focuses on **how text looks**
- Formatting codes are *specific to the editor*, not part of regular text
- Does **not** describe the meaning of content
- ✅ **WYSIWYG** (What You See Is What You Get) → direct visual editing
- **Examples:** MS Word, Google Docs

### 2. Procedural Markup

- Describes **steps or procedures** to format text
- Example instructions:
  - 1️⃣ Change font → make it large and bold
  - 2️⃣ Indent by two lines
- Emphasizes **how to format**, not what the content means

### 3. Descriptive Markup

- Describes the **meaning and structure** of content
- Actual appearance is decided by the **renderer** (browser / compiler)
- ✅ Clear semantic meaning
- ❌ Not WYSIWYG while writing
- Example structure: `<title> with <heading> within 2 <paragraph>s`
- **Examples:** LaTeX, HTML
