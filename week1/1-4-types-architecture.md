
# Architectures
## Client ↔ Server Architecture

```mermaid
sequenceDiagram
    participant Client
    participant Network
    participant Server

    Client->>Network: HTTP Request (GET / POST)
    Network->>Server: Forward request (doesn't modify)

    Server-->>Network: provides HTTP Response (data / status)
    Network-->>Client: Deliver response

    Note over Client: User interaction, display
    Note over Server: Stores data & perform computations
    Note over Network: Connects client to server (can be local)
```


- **Client Machine**: may run without direct user interaction, e.g. software/antivirus updaters running in the *background*
- **Local Systems**: both client & server run on same machine like *browser accessing a local database or `localhost` web server.*
- **Stateless Requests**: The server does not remember previous requests unless extra mechanisms like sessions, cookies, or tokens are used.

## Distributed or peer-to-peer Architecture

- All peers are considered "**equivalent**" so no permanent central controller
  - If a peer fails⚠️, automatically re-selects✅ another peer
  - The system keeps working🔁 even if some peers go offline
- Shared ℹ️information and resources among **peers**
- Ex: *bittorrent, Blockchain, Distributed file systems*

:::info When you download a movie using a torrent:
- You download small pieces of the movie from many users
- At the same time, you upload the pieces you already have to others<br>
👉 So, every downloader also becomes an uploader (Data can flow in both ways)
:::

![architectures](../static/client-peer-architecture.png)
source: https://em360tech.com/tech-articles/client-server-architecture-enterprise-it


::: details Design Pattern
A general, reusable solution to a commonly occurring problem within a given context in software design. 
- Designers observe patterns → guide & reuse for faster development
- <span style="color:rgb(240, 96, 118)"> Indexed Metadata </span>: time and attachments info & type; summarize basic information for tracking
:::

### ⭐Checkout [Model-View-Controller Architecture](../week4/4-database-layer-MODEL#mvc-model-view-controller) from Week-4
