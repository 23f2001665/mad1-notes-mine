# Testing

Now that we have seen the basics of backend + frontend development, we built applications, but didn’t focus on verifying them. Now it's time to learn about testing. Testing is an essential part of software development that helps ensure the quality and reliability of your code. In this section, we will cover the basics of testing, including different types of tests and how to write tests for your applications.

## Classification of Tests

Process of testing can be classified into different types based on different criteria. These classifications are independent dimensions — a test can belong to multiple categories from different bases at once. Here are some common classifications of tests:

## Based on Execution of Code

- **Static Testing**: This type of testing involves analyzing the code without executing it. It includes techniques like code reviews, static code analysis, and linting. Static testing helps identify potential issues in the code, such as syntax errors, coding standards violations, and security vulnerabilities.
- **Dynamic Testing**: This type of testing involves executing the code and observing its behavior. Dynamic testing includes techniques like unit testing, integration testing, system testing, and acceptance testing. Dynamic testing helps identify issues that may arise during runtime, such as logic errors, performance issues, and compatibility problems.

## Based on Access of Code

- **White-box Testing**: This type of testing involves testing the internal structure and logic of the code. Testers have access to the source code and can design test cases based on the code's implementation. White-box testing helps identify issues related to code coverage, such as untested paths and conditions. It also helps identify issues related to code quality, such as code complexity and maintainability.
- **Black-box Testing**: This type of testing involves testing the functionality of the code without having access to the source code. Testers only have knowledge of the input and output of the code and design test cases based on the requirements and specifications. Black-box testing helps identify issues related to user experience and system behavior.
- **Grey-box Testing**: This type of testing is a combination of white-box and black-box testing. Testers have partial access to the source code and can design test cases based on both the internal structure and the functionality of the code. Grey-box testing helps identify issues that may not be easily detected through either white-box or black-box testing alone.

## Based on Coverage

- **Statement Coverage**: This type of testing focuses on ensuring that every statement in the code is executed at least once during testing. Statement coverage helps identify untested code and ensures that all parts of the code are exercised during testing.

**did we run every line of code at least once?**

- **Branch Coverage**: This type of testing focuses on ensuring that every possible branch or decision point in the code is executed at least once during testing. Branch coverage helps identify untested paths and ensures that all possible outcomes of the code are exercised during testing.

**did we run every possible branch in the code at least once?**

- **Path Coverage**: This type of testing focuses on ensuring that every possible path through the code is executed at least once during testing. Path coverage helps identify untested combinations of statements and branches and ensures that all possible scenarios are exercised during testing.

**did we run every possible path through the code at least once?**

- **Condition Coverage**: This type of testing focuses on ensuring that every possible condition in the code is evaluated to both true and false at least once during testing. Condition coverage helps identify untested conditions and ensures that all possible outcomes of the code are exercised during testing.

**did we evaluate every possible condition in the code to both true and false at least once?**

- **Function Coverage**: This type of testing focuses on ensuring that every function or method in the code is executed at least once during testing. Function coverage helps identify untested functions and ensures that all parts of the code are exercised during testing.

**did we run every function or method in the code at least once?**

## Based on Scope

- **Unit Testing**: This type of testing focuses on testing small, isolated units of code, such as functions or methods. Unit tests are typically written by developers and are used to ensure that individual components of the code work as expected.
- **Integration Testing**: This type of testing focuses on testing the interactions between different components of the code. Integration tests are used to ensure that different parts of the code work together correctly.
- **System Testing**: This type of testing focuses on testing the entire system as a whole. System tests are used to ensure that the system meets the specified requirements and behaves as expected in a real-world environment.
- **Acceptance Testing**: This type of testing focuses on testing the system from the perspective of the end user. Acceptance tests are used to ensure that the system meets the needs and expectations of the users and is ready for deployment. This type of testing is often involves user validation (e.g., beta testing and feedback collection).
- **Regression Testing**: This type of testing focuses on testing the system after changes have been made to ensure that existing functionality has not been broken. Regression tests are used to identify and fix any issues that may arise due to code changes or updates.
- **Performance Testing**: This type of testing focuses on testing the performance and scalability of the system under different conditions. Performance tests are used to identify and address any performance bottlenecks or issues that may arise in the system.

## A Few More Things To Note

- **Test-Driven Development (TDD)**: This is a software development approach where tests are written before the actual code is implemented. TDD helps ensure that the code is designed to meet the specified requirements and encourages developers to write clean and maintainable code.
- **Continuous Integration (CI)**: This is a practice where code changes are automatically tested and integrated into the main codebase. CI helps ensure that code changes do not introduce new issues and allows for faster feedback and collaboration among developers.We’ll explore this in more detail later when discussing DevOps.
- **Mocking and Stubbing**: These are techniques used in testing to simulate the behavior of external dependencies or components. Mocking involves creating mock objects that mimic the behavior of real objects, while stubbing involves creating stub functions that return predefined responses. These techniques help isolate the code being tested and allow for more controlled testing scenarios.

  - Stub → returns fixed data
  - Mock → verifies interactions (was function called? with what args?)

- **Test Automation**: This is the practice of using software tools to automate the execution of tests. Test automation helps improve the efficiency and effectiveness of testing by allowing tests to be run quickly and consistently. There are various tools available for test automation, such as Selenium for web applications and JUnit for Java applications.
- **Test Frameworks**: These are software frameworks that provide a structured approach to writing and executing tests. Test frameworks help organize tests, provide assertions for validating test results, and offer features for test reporting and debugging. Some popular test frameworks include Jest for JavaScript, JUnit for Java, and PyTest for Python.

## Tools for testing

We can test at various levels of the software development process, and there are many tools available for testing. Here are some popular tools for testing:

- **Unit Testing**: Jest (JavaScript), JUnit (Java), PyTest (Python)(unittest)
- **API Testing**: Postman, Insomnia, REST Assured, Thunder Client, Curl Scripts
- **End-to-End Testing**: Selenium, Cypress, Playwright
- **Performance Testing**: JMeter, Gatling, LoadRunner
- **Continuous Integration**: Jenkins, Travis CI, CircleCI, GitHub Actions

:::info Pytest

In the next section, we will narrow down our focus to unit testing and learn how to write unit tests using PyTest, a popular testing framework for Python.

:::
