# MilliSec Splunk Detection Rules

Professional Splunk SIEM detection rules managed as code and automatically deployed to Splunk through the REST API.

## Project Objective

This repository is the central source of truth for MilliSec SIEM detection rules.

Detection rules are created and updated in GitHub instead of being manually modified in Splunk. Changes committed to this repository are validated and deployed to Splunk through an automated API-based workflow.

## Architecture

GitHub Repository  
↓  
GitHub Actions  
↓  
Rule Validation  
↓  
Deployment Script  
↓  
Splunk REST API  
↓  
Splunk Detection Rules

## Detection Engineering

The repository contains 15 production-style detection rules covering:

- Web application attacks
- Authentication attacks
- Reconnaissance activity
- Access control violations
- Multi-stage attack correlation

Each rule includes severity, MITRE ATT&CK mapping, data source information, false-positive guidance, investigation steps, response recommendations, scheduling configuration and SPL detection logic.

## Deployment Model

GitHub is used as the source of truth.

Rules must not be manually modified in Splunk. Any rule modification is committed to GitHub and automatically synchronized with Splunk through the REST API.

## Author

**Emin Yahyazadə**  
SOC Analyst / Cybersecurity Intern
