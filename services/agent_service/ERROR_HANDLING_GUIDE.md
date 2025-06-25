# Error Handling Guide for Agent Service

## Overview

This guide explains the comprehensive error handling system implemented in the agent service, designed to provide graceful error handling and meaningful error messages to the frontend.

## Error Structure

All errors follow a standardized structure:

```json
{
  "error": true,
  "message": "Technical error message for logging",
  "user_message": "User-friendly error message",
  "category": "execution|planning|evaluation|external_service|validation|network|timeout|unknown",
  "severity": "low|medium|high|critical",
  "error_code": "EXECUTION_ERROR",
  "details": {
    "source": "github",
    "original_error": "Connection timeout",
    "context": "execution"
  },
  "recoverable": true,
  "type": "ExecutionError",
  "trace_info": {
    // Optional trace information
  },
  "session_id": "user_session_123"
}
```

## Error Categories

### 1. Planning Errors (`planning`)
- **When**: Issues during query planning phase
- **Severity**: High
- **User Message**: "I'm having trouble understanding your request. Could you please rephrase it?"
- **Example**: Invalid query structure, planning timeout

### 2. Execution Errors (`execution`)
- **When**: Issues during query execution phase
- **Severity**: High
- **User Message**: "I encountered an issue while processing your request. Please try again."
- **Example**: Data source failures, aggregation errors

### 3. Evaluation Errors (`evaluation`)
- **When**: Issues during answer evaluation phase
- **Severity**: Medium
- **User Message**: "I'm having trouble evaluating the response quality. The answer may need review."
- **Example**: Evaluation model failures, scoring errors

### 4. External Service Errors (`external_service`)
- **When**: Issues with external services (Notion, GitHub, etc.)
- **Severity**: Medium
- **User Message**: "One of my data sources is temporarily unavailable. Please try again later."
- **Example**: Service outages, API rate limits

### 5. Validation Errors (`validation`)
- **When**: Input validation failures
- **Severity**: Low
- **User Message**: "Please check your input and try again."
- **Example**: Missing required fields, invalid formats

### 6. Network Errors (`network`)
- **When**: Network connectivity issues
- **Severity**: High
- **User Message**: "I'm experiencing network connectivity issues. Please check your connection and try again."
- **Example**: Connection timeouts, DNS failures

### 7. Timeout Errors (`timeout`)
- **When**: Operations exceed time limits
- **Severity**: Medium
- **User Message**: "The request is taking longer than expected. Please try again."
- **Example**: LLM response timeouts, external service timeouts

## Frontend Integration

### JavaScript/TypeScript Example

```typescript
interface AgentError {
  error: boolean;
  message: string;
  user_message: string;
  category: string;
  severity: 'low' | 'medium' | 'high' | 'critical';
  error_code: string;
  details: Record<string, any>;
  recoverable: boolean;
  type: string;
  trace_info?: any;
  session_id?: string;
}

class AgentServiceClient {
  async sendMessage(message: string, sessionId?: string): Promise<any> {
    try {
      const response = await fetch('/api/agent/message', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message,
          session_id: sessionId
        })
      });

      const data = await response.json();

      // Check if response contains an error
      if (data.error) {
        this.handleAgentError(data as AgentError);
        return data;
      }

      return data;
    } catch (error) {
      // Handle network/HTTP errors
      this.handleNetworkError(error);
      throw error;
    }
  }

  private handleAgentError(error: AgentError): void {
    // Log technical details for debugging
    console.error('Agent Error:', {
      message: error.message,
      category: error.category,
      severity: error.severity,
      error_code: error.error_code,
      details: error.details
    });

    // Show user-friendly message
    this.showUserMessage(error.user_message, error.severity);

    // Handle different error categories
    switch (error.category) {
      case 'planning':
        this.handlePlanningError(error);
        break;
      case 'execution':
        this.handleExecutionError(error);
        break;
      case 'external_service':
        this.handleExternalServiceError(error);
        break;
      case 'timeout':
        this.handleTimeoutError(error);
        break;
      case 'validation':
        this.handleValidationError(error);
        break;
      default:
        this.handleGenericError(error);
    }
  }

  private handlePlanningError(error: AgentError): void {
    // Suggest rephrasing the query
    this.showSuggestion('Try rephrasing your question or breaking it into smaller parts.');
  }

  private handleExecutionError(error: AgentError): void {
    // Check if it's recoverable
    if (error.recoverable) {
      this.showRetryButton(() => this.retryLastRequest());
    }
  }

  private handleExternalServiceError(error: AgentError): void {
    const service = error.details?.service;
    if (service) {
      this.showServiceStatus(`${service} service is temporarily unavailable`);
    }
  }

  private handleTimeoutError(error: AgentError): void {
    // Show progress indicator and suggest retry
    this.showTimeoutMessage();
    this.showRetryButton(() => this.retryLastRequest());
  }

  private handleValidationError(error: AgentError): void {
    // Highlight the problematic field
    const field = error.details?.field;
    if (field) {
      this.highlightField(field);
    }
  }

  private showUserMessage(message: string, severity: string): void {
    // Implementation depends on your UI framework
    const alertType = this.getAlertType(severity);
    this.showAlert(message, alertType);
  }

  private getAlertType(severity: string): string {
    switch (severity) {
      case 'critical': return 'error';
      case 'high': return 'error';
      case 'medium': return 'warning';
      case 'low': return 'info';
      default: return 'info';
    }
  }

  private showRetryButton(onRetry: () => void): void {
    // Show retry button in UI
    this.showButton('Retry', onRetry);
  }

  private retryLastRequest(): void {
    // Implement retry logic
    this.sendMessage(this.lastMessage, this.lastSessionId);
  }
}
```

### React Example

```tsx
import React, { useState } from 'react';

interface AgentError {
  error: boolean;
  user_message: string;
  category: string;
  severity: 'low' | 'medium' | 'high' | 'critical';
  recoverable: boolean;
  details: Record<string, any>;
}

const AgentChat: React.FC = () => {
  const [messages, setMessages] = useState<Array<{text: string, isUser: boolean, error?: AgentError}>>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<AgentError | null>(null);

  const sendMessage = async (message: string) => {
    setLoading(true);
    setError(null);

    try {
      const response = await fetch('/api/agent/message', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message })
      });

      const data = await response.json();

      if (data.error) {
        const agentError = data as AgentError;
        setError(agentError);
        
        // Add error message to chat
        setMessages(prev => [...prev, {
          text: agentError.user_message,
          isUser: false,
          error: agentError
        }]);

        // Handle specific error types
        handleSpecificError(agentError);
      } else {
        // Handle successful response
        setMessages(prev => [...prev, {
          text: data.trace_info?.final_answer || 'Response received',
          isUser: false
        }]);
      }
    } catch (networkError) {
      const networkErrorObj: AgentError = {
        error: true,
        user_message: "Network error. Please check your connection and try again.",
        category: "network",
        severity: "high",
        recoverable: true,
        details: { original_error: networkError.message }
      };
      setError(networkErrorObj);
    } finally {
      setLoading(false);
    }
  };

  const handleSpecificError = (error: AgentError) => {
    switch (error.category) {
      case 'timeout':
        // Show retry button
        break;
      case 'external_service':
        // Show service status
        break;
      case 'validation':
        // Highlight input field
        break;
      default:
        // Generic error handling
        break;
    }
  };

  const retryLastRequest = () => {
    const lastUserMessage = messages
      .filter(m => m.isUser)
      .pop()?.text;
    
    if (lastUserMessage) {
      sendMessage(lastUserMessage);
    }
  };

  return (
    <div className="agent-chat">
      <div className="messages">
        {messages.map((msg, index) => (
          <div key={index} className={`message ${msg.isUser ? 'user' : 'agent'}`}>
            <div className="text">{msg.text}</div>
            {msg.error && (
              <div className={`error-banner ${msg.error.severity}`}>
                <span className="error-icon">⚠️</span>
                <span className="error-category">{msg.error.category}</span>
                {msg.error.recoverable && (
                  <button onClick={retryLastRequest} className="retry-btn">
                    Retry
                  </button>
                )}
              </div>
            )}
          </div>
        ))}
      </div>

      {error && (
        <div className={`error-toast ${error.severity}`}>
          <div className="error-message">{error.user_message}</div>
          {error.recoverable && (
            <button onClick={retryLastRequest} className="retry-button">
              Try Again
            </button>
          )}
        </div>
      )}

      {loading && (
        <div className="loading-indicator">
          Processing your request...
        </div>
      )}
    </div>
  );
};
```

## Error Recovery Strategies

### 1. Automatic Retry
For recoverable errors, implement automatic retry with exponential backoff:

```typescript
async function retryWithBackoff<T>(
  fn: () => Promise<T>,
  maxRetries: number = 3,
  baseDelay: number = 1000
): Promise<T> {
  let lastError: Error;
  
  for (let attempt = 0; attempt <= maxRetries; attempt++) {
    try {
      return await fn();
    } catch (error) {
      lastError = error as Error;
      
      if (attempt === maxRetries) {
        throw error;
      }
      
      // Check if error is retryable
      if (isRetryableError(error)) {
        const delay = baseDelay * Math.pow(2, attempt);
        await new Promise(resolve => setTimeout(resolve, delay));
        continue;
      }
      
      throw error;
    }
  }
  
  throw lastError!;
}

function isRetryableError(error: any): boolean {
  const retryableCategories = ['network', 'timeout', 'external_service'];
  return error.category && retryableCategories.includes(error.category);
}
```

### 2. Fallback Responses
For non-critical errors, provide fallback responses:

```typescript
function getFallbackResponse(error: AgentError): string {
  switch (error.category) {
    case 'external_service':
      return "I'm having trouble accessing some information sources, but here's what I can tell you based on available data...";
    case 'evaluation':
      return "I've provided an answer, though I wasn't able to fully evaluate its quality. Please review the information carefully.";
    default:
      return "I encountered an issue while processing your request. Here's the best answer I can provide...";
  }
}
```

## Monitoring and Alerting

### 1. Error Tracking
Track errors for monitoring and debugging:

```typescript
function trackError(error: AgentError): void {
  // Send to monitoring service (e.g., Sentry, DataDog)
  analytics.track('agent_error', {
    category: error.category,
    severity: error.severity,
    error_code: error.error_code,
    session_id: error.session_id,
    details: error.details
  });
}
```

### 2. Error Rate Monitoring
Monitor error rates by category:

```typescript
const errorCounts = {
  planning: 0,
  execution: 0,
  evaluation: 0,
  external_service: 0,
  network: 0,
  timeout: 0
};

function incrementErrorCount(category: string): void {
  if (errorCounts[category] !== undefined) {
    errorCounts[category]++;
  }
  
  // Alert if error rate is too high
  const totalErrors = Object.values(errorCounts).reduce((a, b) => a + b, 0);
  if (totalErrors > 100) {
    alert('High error rate detected');
  }
}
```

## Best Practices

1. **Always show user-friendly messages**: Never expose technical error details to users
2. **Provide recovery options**: Offer retry buttons for recoverable errors
3. **Log technical details**: Keep detailed logs for debugging
4. **Categorize errors properly**: Use appropriate error categories for better handling
5. **Implement timeouts**: Add timeouts to prevent hanging requests
6. **Monitor error rates**: Track error patterns for system health
7. **Graceful degradation**: Provide fallback responses when possible
8. **Session management**: Include session IDs for error tracking

## Testing Error Scenarios

```typescript
describe('Agent Error Handling', () => {
  it('should handle planning errors gracefully', async () => {
    const response = await agentService.sendMessage('');
    expect(response.error).toBe(true);
    expect(response.category).toBe('validation');
    expect(response.user_message).toContain('valid message');
  });

  it('should handle external service errors', async () => {
    // Mock external service failure
    mockExternalServiceFailure();
    
    const response = await agentService.sendMessage('test query');
    expect(response.error).toBe(true);
    expect(response.category).toBe('external_service');
    expect(response.recoverable).toBe(true);
  });

  it('should provide retry options for recoverable errors', async () => {
    const response = await agentService.sendMessage('test');
    if (response.error && response.recoverable) {
      expect(response.user_message).toContain('try again');
    }
  });
});
``` 