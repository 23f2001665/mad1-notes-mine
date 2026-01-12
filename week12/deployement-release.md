# Software Deployment vs Software Release

---

## **Software Deployment**

**Physical act of putting code into an environment**

Think of it as *moving* the new version of the application to servers (production, staging, etc). After deployment:

* The code is present and running somewhere
* It may or may not be visible to users
* Features can be hidden behind flags

**Example:**
The backend team deploys a new payment module to production servers, but keeps it disabled for users.

---

## **Software Release**

**Making the deployed functionality available to users**

Release is about *exposing* the features—letting customers interact with the deployed code.

* Controlled via feature toggles, config switches, UI changes
* Can be gradual (canary releases, beta rollout)
* Can happen **after** deployment

**Example:**
Next day, the team enables the payment module for 5% of users. That’s a release.

---

## **Short Comparison**

| Aspect       | Deployment                     | Release                                  |
| ------------ | ------------------------------ | ---------------------------------------- |
| What it does | Moves code into an environment | Makes features accessible to users       |
| Visibility   | Not necessarily visible        | User-facing                              |
| Timing       | Can be done anytime            | Often after testing or business approval |
| Control      | DevOps/Infrastructure          | Product/Feature management               |

---

## **Analogy**

* **Deployment** = installing a new machine on the factory floor
* **Release** = flipping the switch so customers start using products made by that machine

---

## **In one line**

> **Deployment puts code in production; release decides when users can actually use it.**

---
