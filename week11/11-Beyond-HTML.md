# Beyond HTML
https://www.besanttechnologies.com/wp-content/uploads/2017/12/differences-between-html-and-html5.png
:::tab

== SGML Standardized Generalized Markup Lang
- base form `meta`-language to define other markup languages
	- **Declarative** specify structure & attributes ❌ how to process
	- **Rigorous** strict def of structure `way tag open/close/nested, what kind permitted in diff places`
- DTD **Document Type Definition** → diff families within this umbrella, each /w own **custom tags** interpretation & document behaviour as per needs
- ❌ strict tags `HTML2 aligns with SGML, HTML4 ✅compliant, HTML5 ❌`but designed to be forgiving of errors for accessibility

== XML eXtensible Markup lang
- Human-readable: simple general ❌ predefined usable **custom tags** → multiple applications defined
- Machine readable:✅ complex data structures & relationships
`MathML`
	`RSS` feeds are primarily used to get information about latest updates on a given page(News, blogs)
	`Atom,SVG`Scalable Vector Graphics
- `XHTML= HTML4 + XML Namespaces`  allow inter-operability, modular, extensible

== HTML5
- multimedia support, canvases
- Enhanced APIs for better browser interaction.
- human-machine readable, backward compatible (older tags)
- ❌`XML/SGML` ✅ **own parsing rules**
- maintained by`WHATWG` Web Hypertext Application Technology Working Group `W3C`
- Standard → want New tags/features in ur site? → `JavaScript`, Custom elements `API supported by browsers` → Semantics may ❌ be well thought for `search engine`

:::

# JavaScript
[list2node]

- High lvl prog lang 
	- object orientation `class` 
	- dynamic typing `variables can hold different types❌init type declaration`
	- function composition 
	- imperative procedures
	- Web browser dedicated `js` engine
	- Event-driven Handles `asynchronous` events efficiently (user clicks)

- APIs
	- `text, dates, RegEx`
	- dict/list/array DS
	- [[DOM]] `document object model` real-time interaction /w webpage browser environment
	- ❌ native IO or file access but through external APIs

```js
const para = document.querySelector('p');
para.addEventListener('click', updateName);

function updateName() {
	let name = prompt('Enter a new name');
	para.textContent = 'Player 1: ' + name;
}
```

```html
<button id="button_A">Press me</button>
<h3 id="heading_A"></h3>
```
```js
const buttonA = document.querySelector('#button_A');
const headingA = document.querySelector('#heading_A');

buttonA.onclick = function() {
	let name = prompt ('What is your name?');
	alert('Hello ' + name + ', nice to see you!');
	headingA.textContent = 'Welcome ' + name;
}
```

### Web components
- ❌ HTML5 ✅ XML allows arbitrary namespaces & tag definitions
	- **Render** display details how shown
	- **States** checkbox - blank/checked (custom?)
	- Customized built-in/Autonomous custom element
	- Limited Standardization ✅ reuse 
	- Modular design

:::tabs
== shadow DOM API
keeps styling of component separate from rest of page (restrict scope of modification of content)
```js
const shadowRoot = document.getElementById('example').attachShadow({ mode: 'open' });
shadowRoot.innerHTML = `<style>
button {
color: tomato;
}
</style>
<button id="button">This will use the CSS color tomato <slot></slot></button>`;
```
== Custom Elements (JS API)
	Enhanced APIs for better browser interaction.
```js
<flag-icon country="nl"></flag-icon>
// declare a class for the custom element, extending HTMLElement:

class FlagIcon extends HTMLElement {
	constructor() {
	super();
	this._countryCode = null;
	this._img = document.createElement('img'); // create an img element
	this.attachShadow({ mode: 'open' }).appendChild(this._img); // use shadow DOM to encapsulate styles and markup
	}

	static get observedAttributes() {
	return ["country"];
	}

	attributeChangedCallback(name, oldValue, newValue) {
	// name will always be "country" due to observedAttributes
	this._countryCode = newValue;
	this._updateRendering();
	}

	connectedCallback() {
	this._updateRendering();
	}

	get country() {
	return this._countryCode;
	}

	set country(v) {
	this.setAttribute("country", v);
	}

	_updateRendering() {
	// Check if element is in a document with browsing context
	if (!this.ownerDocument.defaultView) return;
	if (this._countryCode) {
		// Use a source path for flags, here using a free public CDN for country flags as example
		this._img.src = `https://flagcdn.com/w80/${this._countryCode.toLowerCase()}.png`;
		this._img.alt = `Flag of ${this._countryCode.toUpperCase()}`;
		this._img.style.width = '80px';
		this._img.style.height = 'auto';
		this._img.style.display = 'block';
	} else {
		this._img.removeAttribute('src');
		this._img.alt = '';
	}
	}
}

customElements.define("flag-icon", FlagIcon);
// The parser, whenever it sees the flag-icon tag, will construct a new instance of our FlagIcon class, and tell our code about its new country attribute, which we then use to set the element's internal state and update its rendering (when appropriate).
const flagIcon = document.createElement("flag-icon")
flagIcon.country = "jp"
document.body.appendChild(flagIcon)
//  use the custom element constructor itself. above code is equivalent to:

const flagIcon = new FlagIcon()
flagIcon.country = "jp"
document.body.appendChild(flagIcon)
```
== HTML Templates
`<template>` & `<slot>` tags to write markup templates (❌ advanced as jinja). reusable & structured templates for content
```js
<template id="book-template">
	<li><span class="author"></span>'s classic novel <span class="title"></span></li>
</template>

<ul id="books"></ul>

const fragment = document.getElementById('book-template');
const books = [
	{ title: 'The Great Gatsby', author: 'F. Scott Fitzgerald' },
	{ title: 'A Farewell to Arms', author: 'Ernest Hemingway' },
	{ title: 'Catch 22', author: 'Joseph Heller' }
];

books.forEach(book => {
	// Create an instance of the template content
	const instance = document.importNode(fragment.content, true);
	// Add relevant content to the template
	instance.querySelector('.title').innerHTML = book.title;
	instance.querySelector('.author').innerHTML = book.author;
	// Append the instance ot the DOM
	document.getElementById('books').appendChild(instance);
});
//creates a template (<template id="book-template">) without any other Web Components technology,  three technologies in the stack can be used independently or collectively.
```

:::

## [Frameworks](https://developer.mozilla.org/en-US/docs/Learn_web_development/Core/Frameworks_libraries/Introduction)
- Python can create network listeners, basic templates, manipulate strings... `Flask, django`
- JS can extend elements, APIs to manipulate documents `React.js, Angular.js, vue.js, Ember.js (frontend), Next.js, Node.js` 
- SPA: **Single Page Application** ✅ mobile & dynamically update content without reloading.
- Lot of code repetition - **boilerplate** reinventing styles-techniques
- Standard techniques for common problems - **design patterns**



T1 2025
![](../static/Pasted image 20251204173738.png)
T3 2024
![](../static/Pasted image 20251204173858.png)
T2 2024
![](../static/Pasted image 20251204173911.png)
T1 2024
Which of the below JavaScript statement(s) are used to print information on the browser’s console?

Options :
window.alert()
console.log()
document.write()
None of these

:::info Check the following links for more details:
- https://codepen.io/calebdwilliams/pen/rRNJPJ
- https://html.spec.whatwg.org/multipage/custom-elements.html
- https://css-tricks.com/an-introduction-to-web-components/
- https://github.com/mdn/web-components-examples
:::