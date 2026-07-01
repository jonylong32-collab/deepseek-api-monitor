# Security Policy

## Reporting a Vulnerability

Please do not open public issues for credential leaks, API key handling problems, or other security-sensitive reports. Contact the repository owner through GitHub with a private report.

## Sensitive Data

This project is intended to run locally and may handle a user's DeepSeek API Key. The repository must not contain real API keys, `.env` files, WebView profile data, packaged runtime data, or exported usage files that include private account information.

## Local Storage

The app stores configuration in the user's application data directory. API keys are encrypted locally with Fernet before being written to disk.
