# Memory Hierarchy
![](https://cn.edurev.in/ApplicationImages/Temp/1421638_a9fe7b34-1e74-45f4-a8ae-cbbeea02d22a_lg.png?w=360&dpr=2.6)

Modern computers balance **speed, cost, and capacity**.
No single memory type is optimal for all three efficiently, so systems use a layered memory hierarchy:

`Registers → Cache (SRAM) → DRAM → SSD → HDD → Cold Storage`

As we go in this order:
- Latency increases (slower access)
- Throughput decreases (generally)
- Capacity increases
- Cost per bit decreases

[ℹ️Magnetic disk animation](https://youtu.be/ngP6nSt_yAE)<br>
SRAM → **Static** RAM <br>DRAM → **Dynamic** RAM

### Key Performance Metrics
1. **Latency**: time to read 1st byte from storage location (less is better)
`Register < SRAM < DRAM < SSD < HDD`
2. **Throughput** (Bandwidth) $\frac{\text{no. of bytes read}}{\text{second}}$ (more is better)
`DRAM > SSD > HDD (regs, SRAM limited capacity)`
- `DRAM` provides the highest sustained bandwidth for bulk transfers, 
- `Registers` and `SRAM` are extremely fast but limited in size.

3. **Density** $\frac{\text{no. of bits stored}}{\text{cost x unit area}}$ ↑
` Registers < SRAM < DRAM < SSD < HDD`
- Registers are the most expensive per bit, while HDD provides the cheapest large-scale storage

## Storage Elements

<div class="card">
<h4> On-chip Registers (<span style="color:rgb(98, 151, 208)">10–100 Bytes</span>)</h4>
<ul>
<li>Located inside the CPU</li>
<li>Used for immediate computation and instruction execution</li>
<li>Acts as the CPU’s working scratchpad</li>
<li><b>Fastest memory available</b></li>
</ul>
</div>

<div class="card">

<h4>SRAM – Cache Memory (L1, L2, L3) (≈<span style="color:rgb(98, 151, 208)">0.1–1 MB</span>)</h4>
<ul>
<li>Stores frequently accessed data and instructions</li>
<li>Reduces access to slower DRAM</li>
<li>Exploits <b>temporal and spatial locality</b></li>
<li>Very fast but expensive → used in small amounts</li>
</ul>
</div>

<div class="card">
<h4>🔹 DRAM – Main Memory (<span style="color:rgb(98, 151, 208)">0.1-10 GB</span> scale)</h4>
<ul>
<li>Holds active programs and working data</li>
<li>Volatile: data lost when power is off</li>
<li>Slower than cache but much larger</li>
<li>Acts as the primary working memory of the system</li>
</ul>
</div>

<div class="card">
<h4>🔹 SSD – Solid State Drive (<span style="color:rgb(98, 151, 208)">1-100 GB</span> Flash Storage)</h4>
<ul>
<li>Non-volatile storage (data persists without power)</li>
<li>No moving parts → lower latency than HDD</li>
<li>High throughput, used for OS and applications</li>
</ul>
</div>
<div class="card">
<h4>HDD – Magnetic Disk Storage <span style="color:rgb(98, 151, 208)">0.1-10 TB </span></h4>
<ul>
<li>Very high capacity</li>
<li>Uses spinning disks and mechanical read/write heads</li>
<li>High latency due to mechanical movement (disk rotation)</li>
<li>Low cost per GB</li>
</ul>
</div>

## Computer Organization

- CPU operates on data in **registers**
- Backed by `L1, L2, L3` cache (SRAM)
- Backed by several GB of `DRAM` working memory
- Backed by `SSD` for high throughput
- Backed by `HDD` for high capacity
- All are backed by **long-term backup storage**
- This layered design ensures that frequently used data stays closer to the CPU,
minimizing expensive memory accesses.

::: attention Important Formula
$$\text{Bandwidth=(Clock Speed)×(Data Transfers per Clock)×(Bus Width in Bytes)×(Channels)}$$
$$\frac{800 \times 10^6 \times 8 \times 2 \times 2}{10^9}= \frac{25600}{1000}=25.6$$
:::

### Cold storage
- `Amazon Glacier, Google, Azure Archive storage classes` 
	- long term storage backup 
	- Huge amounts of data which are rarely accessed or read.
	- High durability (data rarely lost)
	- Very cheap per GB but you may have to tolerate hours of waiting(<48 Hours) as high read latency 
- `optical, magnetic, holographic`

### Insights for us application development

- Plan the storage needs based on your app growth
- Speed of app depends on type of data and how it is stored:
	- Keep frequently used ("hot") data in faster memory
	- Move rarely used ("cold") data to cheaper storage
- Design app based on data access patterns
- Developer must be aware of options and appropriate databases & engines for their application
- Optimize a balance for `latency` read and `throughput` write speed depending on workload

[ℹ️Cores threading](https://cdn.hashnode.com/res/hashnode/image/upload/v1605989026367/G0PyS99Px.png)

## Data search
`O()` notation means "order of" (approximately)

$O(1) \text{ CONSTANT TIME independent of input size, excellent but not even goes through data } \color{#6297D0} \text{Hash table of value \& check index (hope for unique index)}$

:::details $O(\log_2 N) \text{ grows slowly LOGARITHMIC with input, best in practical} \color{#6297D0} \text{ Binary search sorted array}$
- **sorted array search for a number "X"**: look at middle element in array, 
	- greater than "X"": search in lower half
	- lesser than "X": search in upper half
:::

:::details $O(N) \text{ LINEAR - baseline }\color{#6297D0} \text{search in unsorted array/linked list}$
- Search of element in **unsorted linked list or array**: start from beginning -> stepwise compare each element -> STOP if found and return
:::

$O(N^k) \text{ POLYNOMIAL - not good as input size grows}$

$&O(k^N) \text{ EXPONENTIAL very bad even for reasonably small inputs}$

### arrays
- fixed size, so adding new entries require resizing
- **Maintain sort**: find location -> move all further elements by 1 to create a gap -> insert
- **delete** -> move all entries down by 1 step

![](https://miro.medium.com/0*cKsIBkGxRWujTm_U.jpg)

### Binary Search tree
We need BST as sort by growth of tree  
- fixed size array 
- average search $O(\log N)$
- maintaining sorted order $O(N)$
- append needs new size 
- delete needs move all entries by 1 step


###### Self-balancing trees
a tree tilts to 1 side grow downwards so `Red-Black, AVL, B-tree`.

### Hash table 
- Uses hash function to get an index 
- hope for index to not be occupied already, then you can search in $O(1)$

![](https://upload.wikimedia.org/wikipedia/commons/9/9b/Binary_search_tree_example.gif)

### Databases
- Tables with many columns → want to search quickly:
	- proper **INDEX** which is sorted version of column (same datatype short string/int/date)
- Hash-index  ✅ `pattern%` ❌ `%pattern%` `like other_col`
	- in-memory tables
	- ✅ equality comparisons ❌ range
	- ❌ `ORDER BY`
	- ❌ partial key prefix


# NoSQL
![](https://miro.medium.com/v2/1*_BAww08iGuXsM-bij57eZA.png)
**ACID**: Atomic, Consistent (might sacrifice → eventual), Isolated, Durable
**BASE**: Basically Available, Soft State, Eventually Consistent (high available replication) ❌ Financial ✅ Social media ✅ E-com non-fin parts

[list2node]
- #### Document Databases
	`MongoDB, Couchbase, Amazon DocumentDB` ❌ fixed size table (free-from nesting & structure)
	- JSON k-v pairs: obj, records, structs, lists, arrays, maps, dates
	- structured but each doc has own structure![](https://cs186berkeley.net/notes/assets/images/15-NoSQL/books.json.png)
- #### key-value
	python dictionary, C++ ordered map `DynamoDB, Voldermort, Scalaris,Redis, BerkeleyDB, Memcache`
	- Store using search trees or hash table, ≥ 1 attributes(1/multi-valued)
	- ✅ key lookup ❌ range-type relation queries 
	- ✅**in-memory** queries VERY FAST ❌ complex data objects
- #### column stores
	- ✅Collections of column families(variable $\#\text{cols}$)= $\text{(key,}\underbrace{\text{value)}}_\text{set of related cols}$; each row/record has ≥ 1 kv pairs  `BigTable, Cassandra, HBase`
	  all sparse sorted values of given column family (in 1 disk) very FAST	![](https://miro.medium.com/1*j1mNMkBAPJaeh5RoTdnyeQ.png)
- #### Graphs
	- $G=\overbrace{\underset{\text{property/ID}}{\underset{\downarrow}{(V}} \underset{\text{label/roles}}{\underset{\downarrow}{,E)}}}^\text{k-v pair on both}$social-network outgoing degrees (relations), weight of edges nodes **Path finding**
	- `OrientDB, Neo4J, Amazon Neptune, Info-grid`
- #### Time Series Databases
	- optimized for time-stamped or time series data `log performance analysis, monitoring`
	- `RRDTool, InfluxDB, Prometheus, elasticsearch, grafana`
	- are tracked, monitored, down-sampled, & aggregated over time

- **Redundancy**
	- multiple copies as backup if 1 master fails
- **Replication**
	- ❌ backup but multiple sources of ~ data **server cluster in high speed network in ~ datacenter** for load balancing(❌ overload) but geographically dist (Latency → ↓ consistency)

## Scale-up vs Scale-out

- Scale-up
	- larger machine
	- ↑ RAM
	- faster network, processor
	- machine restart with each scale change
- Scale-out
	- multiple servers
	- hard to get consistency
	- cloud model auto scale-out
	- auto scale-up
![](https://assets.serverwatch.com/uploads/2023/06/fig_a-decision_tree_scale_up_or_scale_out.png)

# Security
**SQL injection:** validation before send to DB query (even b4 HTML or Javascript validation)
- known frameworks ✅ servers with good track record, code audits
- Buffer overflows, input overflows (length of queries → client/server might crash) `google app engine`
- Update all patches on OS-network stack-server, encodings char sets

## HTTPS
client ← secure sockets → server
- **Server certificate:** DNS verified by trusted 3rd party, difficult to spoof, maths properties very ↓ probability of mistakes match.
- ✅ secure link for data transfer❌ validation/safety checks 
- ↑performance overhead or ↓ caching (intermediate proxies can't read packets)

:::info Check the following links for more details:
- [NoSQL](https://www.ml4devs.com/en/articles/datastore-choices-sql-vs-nosql-database/)
- [documentation](https://dev.mysql.com/doc/refman/8.4/en/index-btree-hash.html)
- [Postgres](https://www.postgresql.org/docs/current/geqo.html)
- [Screencasts Intro to FTS](https://www.youtube.com/watch?v=9NQUZgU2mMA&list=PLOXyVgDYMn7exXum694qtcRv7K4joLsH0&index=17)
:::