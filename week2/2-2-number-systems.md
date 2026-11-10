In this page, we will learn about four number systems (base 2, 8, 10, 16) and how to convert them into each other. Try converting from one number system to another and check your answers with the Python one-liners given below!!

> [!TIP]
> **Check your answers in Python:** `bin(45)` → `'0b101101'`, `oct(254)` → `'0o376'`, `hex(254)` → `'0xfe'`, and back with `int('101101', 2)`, `int('376', 8)`, `int('FE', 16)` → `45`, `254`, `254`.


## 💻 Binary Number System  (Base 2)

- **Digits used:** $\{0,1\}$
- **Base:** $2$
- Each digit is called a **bit**
- $2^0,  2^1,  2^2, 2^3,\dots$

### ✅ Example

$$
\begin{align}
11001_2 &= 1\times2^4 + 1\times2^3 + 0\times2^2 + 0\times2^1 + 1\times2^0 \\
&= 16 + 8 + 0 + 0 + 1 \\
&= 25_{10}
\end{align}
$$

### 💡 Why Used?

⚡ Digital circuits & computers work with two voltage levels/logical states:

- ON or YES → 1
- OFF or NO → 0

Foundation of all digital systems: *CPU operations, memory, machine-level code*

> [!WARNING]
> **How Many Values Can Binary Represent?**
>
> With $n$ bits, a binary system can represent $2^n$ possible values (each bit is 0 or 1) <br> In the range (0 to $2^{n} -1$)<br>
> Example: $\text{4 bits} \to 2^4 = \text{ 16 values Range: } \to 0 \text{ to }15$


## 🔷 Octal Number System  (Base 8)

- **Digits used:** $\{0,1,2,3,4,5,6,7\}$
- **Base:** $8$

- **1 octal digit = 3 binary bits**

| Binary | 000 | 001 | 010 | 011 | 100 | 101 | 110 | 111 |
| ------ | --- | --- | --- | --- | --- | --- | --- | --- |
| Octal  | 0   | 1   | 2   | 3   | 4   | 5   | 6   | 7   |

### ✅ Example

$$
\begin{align}
623_8 &= 6\times8^2 + 2\times8^1 + 3\times8^0 \\
&= 384 + 16 + 3 \\
&= 403_{10}
\end{align}
$$

### 💡 Why Used?

- Compact form of binary
- Easier to read than raw bits
- UNIX/Linux file permissions


## 🔢 Decimal Number System (Base 10)

- **Digits used:** $\{0,1,2,3,4,5,6,7,8,9\}$
- **Base:** $10$
- $\text{Position values: } 10^0, 10^1, 10^2, 10^3, \dots$

### 📌 Positional System

The value of a digit depends on **its position**.

### ✅ Example

$$
\begin{align}
384_{10} &= 3\times10^2 + 8\times10^1 + 4\times10^0 \\
&= 300 + 80 + 4 \\
&= 384
\end{align}
$$

### 💡 Why Used?
- Natural for humans (10 fingers) in daily calculations


## 🟣 Hexadecimal Number System  (Base 16)

- **Digits used:** $0-9, A-F$
- **Base:** $16$

`A=10, B=11, C=12, D=13, E=14, F=15`

- **1 hex digit = 4 binary bits**

| Binary | 0000 | 0001 | 1010 | 1111 |
| ------ | ---- | ---- | ---- | ---- |
| Hex    | 0    | 1    | A    | F    |


### ✅ Example
$$
\begin{align}
1C7_{16} &= 1\times16^2 + 12\times16^1 + 7\times16^0 \\
&= 256 + 192 + 7 \\
&= 455_{10}
\end{align}
$$

### 💡 Why Important?

- Very compact form of binary
- Used in **memory addresses**
- **Colors** (`#FF5733`)
- **IPv6**, machine-level debugging


![binary-decimal-conversion](https://dotnettutorials.net/wp-content/uploads/2022/08/word-image-29702-1.png)

### Binary-Decimal Conversion
Each bit represents a power of 2, starting from the rightmost bit (from Least Significant Bit i.e. $2^0$ up to $\to 2^n$)

$$
\begin{align}
&0110 = 0\times 2^0 + 1 \times 2^1 + 1\times {2}^2 + 0 \times 2^3 \\& = 0 + 2 + 4 + 0 = 6\\& \text{So, } {0110}_2 = 6_{10}
\end{align}
$$

| Decimal → Binary                        | Binary → Decimal                  |
| --------------------------------------- | --------------------------------- |
| **Integer part**                        | **Integer part**                  |
| 1. Divide the number by 2 .i.e $\frac{x}{2}$              | 1. Write each bit as a power of 2 .i.e $2^{x}$ |
| 2. Note the remainder                   | 2. Multiply the bit by its power $x$  |
| 3. Divide the quotient again by 2       | 3. Add all values                 |
| 4. Repeat until quotient becomes 0         |                                   |
| 5. Write remainders **bottom → top**    |                                   |
|                                         |                                   |
| **Fractional part** (e.g, 0.625)       | **Fractional part**               |
| 1. Multiply the fraction by 2 .i.e $x \times 2$   | 1. Powers of 2 become **negative** .i.e $2^{-x}$   |
| 2. Note the integer part                | 2. $2^{-1}, 2^{-2}, 2^{-3} \cdots$                  |
| 3. Repeat with the new fraction         |  3.  add all values                                 |
| 4. Write integer parts **top → bottom** |    |

> [!CAUTION]
> **❓Try-It-Yourself**
>
> 1. **Binary → Decimal** $110101_2 =  ?$
> 2. **Decimal → Binary** $45_{10} =  ?$
>
> check your steps with the Python one-liners at the top of this page.

## 🔁 Other Conversions (Quick Rules)

> [!NOTE]
> **3. Binary ${11011010}_{2}$ → Hexadecimal**
>
> 1. Group bits in **4s** (right to left) $1101 \quad 1010$
> 2. Convert each group
>
> | Binary | Hex |
> | ------ | --- |
> | 1101   | D   |
> | 1010   | A   |
>
> $${11011010}_{2} = {DA}_{16}$$

> [!NOTE]
> **4. Decimal ${254}_{10}$ → Hexadecimal**
>
> 1. Divide the decimal number by **16**
> 2. Record the Remainders (0-9, A-F) 
> 3. Continue dividing the quotient by 16 until the quotient is 0.
> 4. The hexadecimal number is the remainders read from bottom to top.
>
> | Division | Quotient | Remainder |
> | -------- | -------- | --------- |
> | 254 ÷ 16 | 15       | 14 (E)    |
> | 15 ÷ 16  | 0        | 15 (F)    |
>
> $${254}_{10} = FE_{16}$$

> [!NOTE]
> **5. Binary ${10111101}_{2}$ → Octal**
>
> 1. Group bits in **3s** (right to left, pad the left group with zeros) $010 \quad 111 \quad 101$
> 2. Convert each group
>
> | Binary | Octal |
> | ------ | ----- |
> | 010    | 2     |
> | 111    | 7     |
> | 101    | 5     |
>
> $${10111101}_{2}={275}_8$$

> [!NOTE]
> **6. Octal ${572}_8$ → Decimal**
>
> $$\begin{align}
> &{572}_8 = 5 \times 8^2 + 7 \times 8^1 + 2 \times 8^0 \\& = 5 \times 64 + 7 \times 8 + 2 \times 1 \\& = 320 + 56 + 2 \\& {572}_8 = {378}_{10}
> \end{align}
> $$

> [!NOTE]
> **7. Hexadecimal ${9B}_{16}$ → Decimal**
>
> 1. Write hexadecimal digits with their decimal values
>
> | Hex | Decimal |
> | --- | ------ |
> | 9   | 9   |
> | B   | 11   |
>
> 2. Multiply each hexadecimal digit by $16^{n}$, where $n$ is the position of the digit (starting from $0$ on the right).
>
> 3. Add all the results to get the decimal value.
>
> $$
> \begin{align}
> &{9B}_{16} = 9 \times 16^1 + 11 \times 16^0 \\& = 144 + 11\\
> &{9B}_{16} = {155}_{10}
> \end{align}
> $$

> [!CAUTION]
> **❓Try-It-Yourself**
>
> 3. **Binary → Hexadecimal** $11101101_2 =  ?$
> 4. **Octal → Decimal** $624_8 =  ?$
> 5. **Hexadecimal → Binary** $3F_{16} = ?$

<details>
<summary>Answers to all Try-It-Yourself questions</summary>

1. $110101_2 = 32 + 16 + 4 + 1 = 53_{10}$
2. $45_{10} = 101101_2$
3. $11101101_2 = 1110 \quad 1101 = ED_{16}$
4. $624_8 = 6 \times 64 + 2 \times 8 + 4 = 404_{10}$
5. $3F_{16} = 0011 \quad 1111 = 111111_2$

</details>

> [!TIP]
> **⚡ Shortcut Rule**
>
> Binary ↔ Octal ↔ Hexadecimal conversions can be done **directly**
> using grouping because:
> - 1 octal digit = 3 binary bits
> - 1 hex digit = 4 binary bits
>
> Division method is **NOT used** here.
