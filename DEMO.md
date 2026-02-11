# Demo Guide & Test Scenarios

Use these test queries to demonstrate the capabilities of the Advanced RAG System.

## 1. Document Q&A (Knowledge Base)
**Goal:** Verify the system can answer questions from uploaded documents.

*   "What is a Fraud Analyst?" (If using the Fraud Analyst Guide)
*   "Summarize the key risk controls mentioned in the document."
*   "What are the reporting requirements for suspicious activity?"

## 2. Web Search (Real-time Info)
**Goal:** Verify the system can fetch external information not in the documents.

*   "What's the latest AI news in 2026?"
*   "Current trends in fintech fraud detection."
*   "Who won the Super Bowl in 2025?"

## 3. Hybrid Queries (Docs + Web)
**Goal:** Verify the system can combine internal knowledge with external context.

*   "How do the fraud patterns in my document compare to 2026 trends?"
*   "What new technologies mentioned online could improve the risk controls described in the guide?"

## 4. Complex Reasoning
**Goal:** Test the "Re-ranking" and "Generation" agents.

*   "Based on the documents, create a step-by-step plan for handling an account takeover."
*   "Compare the false positive rates of different detection methods."

## 5. Conversation Memory
**Goal:** Verify context retention.

*   **User:** "Tell me about synthetic identity fraud."
*   **Assistant:** (Answers)
*   **User:** "How do we prevent **that**?" (System should know "that" refers to synthetic identity fraud)
