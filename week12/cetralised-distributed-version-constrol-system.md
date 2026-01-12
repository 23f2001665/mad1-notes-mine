# Centralized vs Distributed Version Control System

---

## **Centralized Version Control System (CVCS)**

### **Idea**

There is **one central server** that stores the entire codebase. Developers connect to this server and pull/push changes.

### **How it works**

* Single repository hosted on a central machine
* Developers need network access to commit or update
* History mainly exists **on the server**

### **Examples**

* **SVN (Subversion)**
* **Perforce**
* **CVS**

### **Pros**

* Simple to understand
* Easy access control (everything is in one place)
* Good for teams that require strict central governance

### **Cons**

* **Single point of failure** — if server goes down, no one can work
* Must be online to commit
* Merging and branching often painful and slower

---

## **Distributed Version Control System (DVCS)**

### **Idea**

Every developer has a **full copy** of the repository, including the entire history. The central server is optional.

### **How it works**

* Each clone = full repository + history
* Commits can be done **offline**
* Changes are later pushed to a shared remote repo

### **Examples**

* **Git**
* **Mercurial**
* **Bazaar**

### **Pros**

* No single point of failure
* Offline commits, diffs, and branching
* Fast operations (local histories)
* Easier and more flexible branching/merging

### **Cons**

* Larger initial clone (copies the whole history)
* Slightly more complex conceptually for beginners

---

## **Quick Comparison Table**

| Feature                 | Centralized VCS            | Distributed VCS                 |
| ----------------------- | -------------------------- | ------------------------------- |
| Repository location     | One central server         | Every developer has a full copy |
| Commit possible offline | ❌ No                       | ✅ Yes                           |
| Single point of failure | ❌ Yes                      | ✅ No                            |
| Speed                   | Slower (network dependent) | Faster (local ops)              |
| Branching/Merging       | Harder, less common        | Efficient, encouraged           |
| Examples                | SVN, CVS                   | Git, Mercurial                  |

---

## **One-liner summary**

> **Centralized VCS relies on a single master repository for version control, while Distributed VCS gives every developer a complete local copy, enabling offline work and more robust, flexible workflows.**

---
