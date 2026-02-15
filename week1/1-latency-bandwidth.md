### ⭐ Checkout [Important metrics & unit conversions](../week0/0-metrics.md) from Week-0

## 🕔 Latency (Time delay)

Latency is the time delay between sending a request and receiving the response.

How long it takes for data to travel from client → server?

- Speed of light in vacuum $\approx 3 \times 10^8 \text{ m/s}$
- Speed in copper/fiber cables $\approx 2 \times 10^8 \text{ m/s}$

**Rule of thumb:**

- ≈ 5 nanoseconds per meter
- ≈ 5 milliseconds per 1000 km

If communication is **continuous request–response** based:

- A new request is sent **only** after the previous response is received
- So latency directly limits how many requests per second are possible

### Problem 1: A student in Chennai is attending an online exam hosted on a server in Delhi.

- Distance between client and server = 2000 km i.e. $2000 \times 10^3$ m
- Signal speed through cables $= 2 \times 10^8 \text{ m/s}$

>How long does the data take to reach the server? (one way in milliseconds)
>Even though it feels “instant”, the signal still has to physically travel through cables.<br>
>So, we use basic `Speed=Distance/Time` physics formula from our School Science textbooks!!😃
>just rearrange it:
$$\begin{gather} \text{ Time } = \frac{\text{Distance}}{\text{Speed}} \\ \frac{2000 \times 10^3}{2 \times 10^8} \\ = 1 \times 10^{-2} = 10\text{ milliseconds}\end{gather}$$
this is **one-way latency**

Calculate the round-trip delay (in ms) i.e. time to go + come-back
In real applications:

- Request goes student → server (2000 km)
- Response comes back server → student (+2000 km)<br>
So data travels twice the distance, hence **twice the time**
$$2 \times \text{10 ms = 20 ms}$$

What is the maximum number of requests per second the client can make? If the student waits for the response before sending the next request

- One request takes Round-trip time
- Only after Round-Trip is finished, the next request starts

So in 1 second, the number of requests possible is:
$$\begin{gather} \text{Requests per second} \approx \frac{1}{\text{Round-trip latency}} \\ = \frac{1}{\text{20 ms}} = \frac{1}{0.02} =
\text{50 requests/sec} \end{gather}$$
👉 Even if student has **high bandwidth or Fast CPU**, Latency still limits how many requests you can do per second, 
This is why:
1. Far-away servers feel slower
2. Databases use [caching](https://developer.mozilla.org/en-US/docs/Web/Progressive_web_apps/Guides/Caching#/)
3. [CDNs](https://developer.mozilla.org/en-US/docs/Glossary/CDN#/) exist

## 🌐 Bandwidth

Bandwidth is how much data can be sent per second.
- Each request sends some amount of data
- Multiple requests per second = more data per second

So total data sent per second is:
$$
\text{Bandwidth} = (\text{Number of requests per second }) \times (\text{size of each request})
$$

Problem 2: A **course-selling portal** allows students to search for courses:
- HTML + CSS + JS = 18 KB
- HTTP headers = 200 B
- Total response size ≈ 18.2 KB

During peak time:
- 1,000 students are searching
- Each user makes 2 searches per second

> How many requests per second does the server receive? (Each student makes `2 requests/sec`)
  $$\begin{gather}
  \text{number of students $\times$ requests per student}\\
  1000 \times 2 = 2000 \text{ requests/sec}
  \end{gather}
  $$

> How much data (in MB per second) does the server send?
  $$\begin{gather}
  \text{total requests/sec $\times$ each request data size
  }\\
  2000 \times 18.2 \text{ KB} = 36{,}400 \text{ KB/s} \\=  36.4 \text{ MBps}
  \end{gather}
  $$

> What is the minimum bandwidth (in Mbps) required? (1 Byte = 8 bits)
  Networks measure bandwidth in bits, not bytes
  $$
  36.4 \times 8 = 291.2 \text{ Mbps}
  $$
  👉 Server needs at least **300 Mbps bandwidth** is needed to avoid congestion.

Gamer streams a **live event** using own streaming server.

- Number of viewers = 50,000
- Each viewer needs a a **4 MB buffer** on the server (few seconds of video so it doesnt buffer when viewer is playing the video)

> How much total memory (in GB) is required?
50,000 viewers are **active at the same time** (memory needs to be store **simultaneously**)
Then server must hold:
$$\begin{gather}
\text{Total Memory = No. of viewers $\times$ video playback buffer memory per viewer} \\
50{,}000 \times 4 \text{ MB} = 200{,}000 \text{ MB}
\\ = 200 \text{ GB}
\end{gather}
$$

> Why is it impractical to handle this using a single server?

- RAM requirement is very high
- Network bandwidth can restrict you.
- One server failure stops the game stream⁉️

Explain why:
Increasing bandwidth does not always reduce page loading time.

| Concept       | Meaning                              |
| ------------- | ------------------------------------ |
| **Latency**   | How fast data travels (time delay)   |
| **Bandwidth** | How much data can be sent per second |

 ⚠️Latency limits the number of requests per second, while bandwidth limits the amount of data per second.

For more numericals to practice, refer to Week 1 instructor sessions:

[link](https://drive.google.com/file/d/1WzbE5AQ08NXfRE6adb7sggVSy6yndeY2)
