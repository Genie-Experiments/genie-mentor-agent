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

## Frontend Integration

### Basic Error Handling

```typescript
interface AgentError {
  error: boolean;
  user_message: string;
  category: string;
  severity: string;
  recoverable: boolean;
}

// Handle API response
if (response.error) {
  showUserMessage(response.user_message);
  
  if (response.recoverable) {
    showRetryButton();
  }
  
  // Log for debugging
  console.error('Agent Error:', response);
}
```

### React Component Example

```tsx
const AgentChat = () => {
  const [error, setError] = useState(null);

  const handleError = (error) => {
    setError(error);
    showAlert(error.user_message, error.severity);
    
    if (error.recoverable) {
      showRetryButton();
    }
  };

  return (
    <div>
      {error && (
        <div className={`error-banner ${error.severity}`}>
          {error.user_message}
          {error.recoverable && <button onClick={retry}>Retry</button>}
        </div>
      )}
    </div>
  );
};
```

## Error Recovery

### Retry Strategy
- **Automatic retry** for `network`, `timeout`, `external_service` errors
- **Manual retry** button for user-initiated retries
- **Exponential backoff** for automatic retries

### Fallback Responses
- Use partial results when some sources fail
- Provide helpful error messages
- Suggest alternative actions

## Best Practices

1. **Show user-friendly messages** - Never expose technical details
2. **Provide retry options** for recoverable errors
3. **Log technical details** for debugging
4. **Categorize errors properly** for better handling
5. **Implement timeouts** to prevent hanging requests
6. **Monitor error rates** for system health

## Quick Reference

### Common Error Scenarios

| Scenario | Error Type | Action |
|----------|------------|--------|
| User sends empty message | `validation` | Show input validation message |
| GitHub API is down | `external_service` | Show service unavailable message |
| Request times out | `timeout` | Show retry button |
| Network connection lost | `network` | Show connection error message |

### Frontend Actions by Severity

| Severity | UI Action |
|----------|-----------|
| `low` | Info notification |
| `medium` | Warning banner |
| `high` | Error banner with retry |
| `critical` | Full error page |

## Testing

```typescript
// Test error handling
it('should handle external service errors', async () => {
  const response = await agentService.sendMessage('test');
  expect(response.error).toBe(true);
  expect(response.category).toBe('external_service');
  expect(response.recoverable).toBe(true);
});
```

---

**Remember**: Always show user-friendly messages and provide recovery options when possible. 