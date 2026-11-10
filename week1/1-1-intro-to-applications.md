# App

An **application (app)** is a computer program designed to perform a specific task for users.
The word started as a short form of "application software", i.e. any desktop program. With the rise of "App stores" for smartphones, it came to mean mostly the lightweight mobile and web applications that can be easily downloaded and installed.

## Platforms

| **Aspect / Feature**        | **Desktop Applications**                                          | **Mobile Applications**                                                   | **Web Applications**                                        |
| --------------------------- | ----------------------------------------------------------------- | ----------------------------------------------------------------- | ----------------------------------------------------------- |
| **Execution Model**         | Standalone apps installed on a PC                                 | Installed apps that frequently communicate with servers, few may work **offline** | runs inside a browser                                       |
| **Examples**                | MS Word, Photoshop, VLC Media Player                              | Instagram, Google Maps                                            | Gmail, Google Docs, YouTube                                 |
| **Data Storage**            | Mostly local storage + optional network sync *Excel*              | Limited local storage (like *WhatsApp chats synced to cloud*)     | Mostly server-side storage (CLOUD datacenters *Google Drive*) |
| **Hardware Constraints**    | High CPU, memory, disk available                                  | Limited screen, battery, memory, processing power                 | Depends on server power, client is lightweight              |
| **SDK/ Development**        | OS-specific *Windows* SDK, macOS *Cocoa*                          | OS-specific: Android SDK (Kotlin/Java), iOS SDK (Swift), or cross-platform like *Flutter* | across OS & devices: Frontend:*Vue, React* + Backend: *Flask, Django* |
| **User Interaction**        | *Keyboard, mouse, files, folders*                                 | *Touch, audio, tilt gestures, camera*                             | *browser-based UI*                                          |

**Embedded devices:** single function, limited scope

```mermaid
flowchart TD
A["Components"]
A --> S["<b>Storage</b>"]
A --> C["<b>Compute</b>"]
A --> P["<b>Presentation</b>"]
```

### SDK (Software Development Kit)

- **Libraries/APIs** → Ready-made code you can reuse instead of writing everything from scratch.
- **Compiler/build tools** → turn your source code into runnable programs.
- **Debuggers** → To find and fix errors.
- **Documentation + Examples →** To guide you on how to use the tools.
- **Emulators / Simulators** → Let you test apps without real devices (Android SDK has phone emulator).
