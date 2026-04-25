# JavaScript

JavaScript is a **high-level, interpreted programming language** primarily designed to enable interactive and dynamic behavior in web browsers.

Unlike languages focused only on computation, JavaScript is tightly integrated with the execution environment (the browser), allowing it to control and modify web pages in real time. 

> Javascript Characteristics
> 1. **High-Level Language**: `JavaScript` abstracts low-level details like memory management and hardware interaction.
> - Developers can focus on **logic and behavior** and worry less about system-level operations
> - Managed automatically by the engine (e.g., garbage collection)
> 2. **Dynamic Typing**: A variable can hold different data types during execution. Type is determined at runtime, not compile time
> - No explicit type declaration required
> 3. **Object-Oriented (Prototype-Based)**: Objects inherit directly from other objects
> No strict requirement for classes like `Java`
> 4. **Multi-Paradigm Language**
> - **Imperative**: Step-by-step instructions on how to perform tasks
> - **Functional**: Functions can be passed as arguments and returned from other functions
> - **Event-Driven**: Handles `asynchronous` events like *clicks, keyboard input, network responses*
> 4. Runs directly inside browsers through engines like: 
> - `V8` Engine (Chrome, Edge)
> - `SpiderMonkey` (Firefox)
> 5. **APIs** with wide range of tools:
>	- `text, dates, RegEx` manipulations like `day.js`
>	- dict/list/array standard data structures
>	- `document object model` real-time interaction with browser environment
>	- We can do input/output or file access thru APIs (no Native support)


## Why DevTools is Useful

Using browser Developer Tools is essential because it gives you direct visibility into how a web application works internally, which is otherwise hidden behind the UI.

1. **Storage (Cookies, Local Storage)**
Websites store data in your browser (e.g., login sessions, preferences)
- View cookies (session IDs, auth tokens) to understand how the website is being authenticated and current user state
- Inspect `local/session storage`

<span style="color:rgb(181, 118, 244)">You can check if a site stores a session_id cookie after login</span>

2. **Network Tab (Data Flow)**
Shows all requests between browser and server like `fetch`ed APIs, images, scripts, files
- See where data comes from and use it
- Inspect request/response payloads and `headers`
- Debug why your requests failed

<span style="color:rgb(181, 118, 244)">Click a button → Network tab shows an API call → You can inspect the JSON response</span>

3. **Console (Debugging & Execution)**
The console acts as a live JavaScript environment, helping you understand how code interacts with the page and how the browser executes scripts internally.
- Run code instantly
- See errors and warnings (debug code)
- Inspect variables and objects
Critical for testing small code snippets

<span style="color:rgb(181, 118, 244)">If your script fails, the console shows the exact error and line number.</span>



> DevTools transforms the browser from a black box into a transparent system, allowing developers to observe, test, and debug every layer of a web application.
> 1. Press `F12/ Ctrl + I` or Right Click → Inspect
> 2. go to the Console tab.
> ![](https://www.debugbear.com/dimg/d6d5a84647077293dbcb3aaae9958498.png)
> For a guided introduction, refer to: https://www.debugbear.com/blog/chrome-browser-console
> For javascript syntax and behaviour, refer to: [JavaScript Basics](../week8/8-javascript-basics.md)
