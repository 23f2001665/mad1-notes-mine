# Security: Sessions, HTTPS & Access Control
<SessionResources :week="6" />

This week answers a core systems question:
> **How does a web application identify users, control access, and keep communication secure?**

So far, you learned how to assign role and access to usernames in your flask app and create forms.
Now we go one step further:
> **How do we securely maintain that identity across multiple requests—and protect it from attacks?**

We connect three key ideas:
- **Access Control → Who is allowed**
- **Sessions & Cookies → Who you are across requests**
- **HTTPS → How data is protected in transit**

We also introduce **logging**, which helps detect failures, attacks, and unusual system behavior.


### Topics Covered

- [Access Control & Security Mechanisms](9-access-security-mechanisms.md)  
  Understand authentication methods, tokens, permissions vs policies, and how systems enforce **who can access what**

- [HTTPS & Logging](9-https-logging.md)  
  Learn why HTTP is insecure, how **TLS encryption and certificates** establish trust, and how logging helps in debugging, monitoring, and detecting attacks  

- [Sessions, Cookies & Web Attacks](9-cookie.md)  
  Understand how sessions maintain user identity, where data is stored, and how attacks like **cookie theft and CSRF** work (and how to prevent them)

- [Flask login](9-flask-login.md)
  session in flask, `flask_login` functionalities, hashing passwords, glimpse upon csrf and token based implementation

### By the End of This Week

You will clearly understand:
- How login systems persist identity using **sessions and cookies**  
- Why storing sensitive data on the client is dangerous  
- How **HTTPS prevents interception and tampering**  
- How attackers exploit weak designs (CSRF, session hijacking)  
- How **logging helps detect and analyze real-world issues**  

This forms the foundation of **secure web application design**—combining identity, access, and communication into one cohesive system.