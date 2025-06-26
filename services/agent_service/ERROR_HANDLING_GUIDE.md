# Error Handling Guide for Agent Service

## Overview

This guide explains the error handling system for the agent service. All errors follow a standardized structure for consistent frontend handling.

## Error Response Structure

```json
{
  "error": true,
  "message": "Technical error for logging",
  "user_message": "User-friendly error message",
  "category": "execution|planning|evaluation|external_service|validation|network|timeout",
  "severity": "low|medium|high|critical",
  "error_code": "EXECUTION_ERROR",
  "recoverable": true,
  "details": { "source": "github" }
}
```

## Error Categories

| Category | When It Occurs | User Message | Severity |
|----------|----------------|--------------|----------|
| `planning` | Query planning fails | "I'm having trouble understanding your request. Please rephrase it." | High |
| `execution` | Data source execution fails | "I encountered an issue while processing your request. Please try again." | High |
| `evaluation` | Answer evaluation fails | "I'm having trouble evaluating the response quality." | Medium |
| `external_service` | Notion/GitHub services down | "One of my data sources is temporarily unavailable." | Medium |
| `validation` | Invalid input | "Please check your input and try again." | Low |
| `network` | Connection issues | "I'm experiencing network connectivity issues." | High |
| `timeout` | Request takes too long | "The request is taking longer than expected." | Medium |
