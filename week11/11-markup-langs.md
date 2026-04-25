# Markup Languages

<div class="card">
  <h2>SGML (Standard Generalized Markup Language)</h2>
  <p>SGML is a `meta`-language used to define other markup languages. Instead of providing predefined tags, it allows users to design their own markup systems.</p>
  <p><strong>Use case:</strong> Developed for large-scale document management (books, technical manuals, government records), where structure and consistency were more important than visual display.</p>
  <p><strong>Key Idea:</strong> Separate <em>content structure</em> from <em>presentation</em>.</p>
  <h3>Syntax Format Example</h3>
  <pre><code>
&lt;!DOCTYPE letter [
  &lt;!ELEMENT letter (to, from, body)&gt;
  &lt;!ELEMENT to (#PCDATA)&gt;
  &lt;!ELEMENT from (#PCDATA)&gt;
  &lt;!ELEMENT body (#PCDATA)&gt;
]&gt;
</code></pre>

<h4>Document Instance (Actual Data)</h4>
<pre><code>
&lt;letter&gt;
  &lt;to&gt;Alice&lt;/to&gt;
  &lt;from&gt;Bob&lt;/from&gt;
  &lt;body&gt;Hello!&lt;/body&gt;
&lt;/letter&gt;
</code></pre>
  <p><strong>Explanation:</strong> SGML first defines rules using a DTD, then documents must strictly follow that structure. So it is:</p>
  <ul>
  <li><strong>Declarative</strong> specify structure & attributes (not how to process them)</li>
  <li><strong>Rigorous</strong> strict definition of structure (what way to nest tags and at what places)</li>
</ul>
  <p><span style="color:rgb(240, 96, 118)">Limitations: Extremely complex, strict, and difficult to implement → unsuitable for the web.</span></p>
</div>

<div class="card">
  <h2>XML (eXtensible Markup Language)</h2>

  <p>XML is a simplified subset of SGML designed</p>
  <p>Tags are custom-defined, but must follow strict rules (proper nesting, closing tags).</p>
  <p><strong>Use case:</strong> Enable systems to exchange data in a structured, predictable format across platforms.</p>

  <p><strong>Key Idea:</strong> User-defined tags + strict structure = reliable data exchange.</p>

  <h3>Syntax Format Example</h3>
  <pre><code>
&lt;book&gt;
  &lt;title&gt;Computer Networks&lt;/title&gt;
  &lt;author&gt;Tanenbaum&lt;/author&gt;
  &lt;year&gt;2011&lt;/year&gt;
&lt;/book&gt;
  </code></pre>

  <p><strong>Where Used:</strong></p>
  <ul>
    <li>APIs and configuration files</li>
    <li>RSS feeds (news or blog updates)</li>
    <li>SVG (graphics), MathML</li>
  </ul>

  <p><strong>Strength:</strong> Both human-readable and machine-readable.</p>
</div>

<div class="card">
  <h2>XHTML= XML + HTML4 (Extensible HyperText Markup Language)</h2>

  <p>XHTML is HTML rewritten using XML rules to enforce stricter structure and consistency.</p>

  <p><strong>Use Case:</strong> Fix the inconsistencies of HTML and make it more extensible by applying XML’s strict syntax rules.  </p>
  <p>`XML Namespaces` allows inter-operable with other XML-based application</p>

  <p><strong>Why It Failed:</strong> Too strict — even small mistakes break the entire page, making it impractical for real-world web development.</p>
</div>

![](https://www.besanttechnologies.com/wp-content/uploads/2017/12/differences-between-html-and-html5.png)

<div class="card">
  <h2>HTML5 (HyperText Markup Language)</h2>

  <p>HTML5 is the modern standard for structuring and displaying web content with own parsing rules.</p>

  <p><strong>Use case:</strong> Provide a flexible, feature-rich system for building modern web applications.</p>

  <p><strong>Key Idea:</strong> Practicality over strictness — browsers should handle errors gracefully.</p>

  <h3>Syntax Format Example</h3>
  <pre><code>
&lt;!DOCTYPE html&gt;
&lt;html&gt;
  &lt;head&gt;
    &lt;title&gt;HTML5 Page&lt;/title&gt;
  &lt;/head&gt;
  &lt;body&gt;
    &lt;header&gt;My Site&lt;/header&gt;
    &lt;article&gt;
      &lt;h1&gt;Welcome&lt;/h1&gt;
      &lt;video controls&gt;
        &lt;source src="video.mp4" type="video/mp4"&gt;
      &lt;/video&gt;
    &lt;/article&gt;
  &lt;/body&gt;
&lt;/html&gt;
  </code></pre>

  <p><strong>Explanation:</strong> Unlike XML/XHTML, HTML5 allows minor syntax errors and still renders correctly. Stays <b>backward compatible</b> with older HTML tags</p>

  <p><strong>Features:</strong></p>
  <ul>
    <li>Multimedia support (audio/video)</li>
    <li>Semantic elements (&lt;header&gt;, &lt;article&gt;)</li>
    <li>APIs for web apps in browser</li>
	<li>New tags or features via `JavaScript`, custom elements</li>
  </ul>

  <p><strong>Maintained by:</strong>`WHATWG` Web Hypertext Application Technology Working Group `W3C`
  </p>
</div>

Both HTML & XML are human and machine readable, 
| **Feature**       | **SGML**              | **XML**       | **XHTML**            | **HTML5**       |
|-------------------|-----------------------|---------------|----------------------|-----------------|
| Type              | Meta-language         | Data markup   | HTML (XML-based)     | Web markup      |
| Primary Use       | Define markup systems | Data exchange | Structured web pages | Modern web apps |
| Syntax Strictness | Very strict           | Strict        | Very strict          | Lenient         |
| Custom Tags       | Yes                   | Yes           | Limited              | Via JavaScript  |
| Error Handling    | No tolerance          | No tolerance  | No tolerance         | Forgiving       |
| Current Relevance | Obsolete              | Still used    | Rare                 | Dominant        |

