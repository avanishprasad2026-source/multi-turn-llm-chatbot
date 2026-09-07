# AI-2: Prompt Engineering Report

**Author:** Avanish Prasad  
**Model Used:** Gemini 1.5 Flash (via Google AI Studio)  

---

## 1. Zero-Shot vs. Few-Shot Comparison

### Task
Categorizing customer feedback into `[Technical, Billing, Feature Request, Praise]` and assigning a priority rating `[Low, Medium, High]`.

### Zero-Shot Prompt
> Classify the following customer feedback into a category (Technical, Billing, Feature Request, Praise) and priority (Low, Medium, High):
> 
> "The export button is grayed out whenever I try to download my monthly transaction logs."

**Raw Output:**
> Category: Technical
> Priority: High - The user is unable to export important logs, which hinders functionality.

---

### Few-Shot Prompt (3 Examples)
> Classify customer feedback into a category (Technical, Billing, Feature Request, Praise) and priority (Low, Medium, High). Format strictly as: Category | Priority.
> 
> Example 1:
> Input: "I was double charged on my last invoice."
> Output: Billing | High
> 
> Example 2:
> Input: "Love the new dark mode theme!"
> Output: Praise | Low
> 
> Example 3:
> Input: "Can you add an option to schedule automated report generation?"
> Output: Feature Request | Medium
> 
> Input: "The export button is grayed out whenever I try to download my monthly transaction logs."
> Output:

**Raw Output:**
> Technical | High

### Analysis
Zero-shot provided a correct classification but included unrequested explanation text. Few-shot enforcement guided the model to strictly follow the desired `Category | Priority` format without additional conversational fluff.

---

## 2. Chain-of-Thought (CoT) Prompting

### Task
Multi-step math word problem requiring order-of-operations and unit conversion logic.

**Problem:**
> A server processes 150 requests per minute during normal hours and 3 times that amount during peak hours. If peak hours last for 4 hours a day and normal hours run for 12 hours a day, how many total requests does the server process in a 5-day work week?

---

### Direct Prompt
> Solve this problem and provide the final answer directly:
> A server processes 150 requests per minute during normal hours and 3 times that amount during peak hours. If peak hours last for 4 hours a day and normal hours run for 12 hours a day, how many total requests does the server process in a 5-day work week?

**Raw Output:**
> Total requests processed in a 5-day work week: 630,000 requests.

*(Analysis: Incorrect — skipped converting hours to minutes or miscalculated peak rate scaling).*

---

### Chain-of-Thought Prompt
> Solve the following problem step by step before giving your final answer:
> A server processes 150 requests per minute during normal hours and 3 times that amount during peak hours. If peak hours last for 4 hours a day and normal hours run for 12 hours a day, how many total requests does the server process in a 5-day work week?

**Raw Output:**
> 1. **Normal Rate**: 150 requests/min = 150 * 60 = 9,000 requests/hour.
> 2. **Peak Rate**: 3 * 150 = 450 requests/min = 450 * 60 = 27,000 requests/hour.
> 3. **Daily Normal Volume**: 9,000 * 12 hours = 108,000 requests/day.
> 4. **Daily Peak Volume**: 27,000 * 4 hours = 108,000 requests/day.
> 5. **Total Daily Volume**: 108,000 + 108,000 = 216,000 requests/day.
> 6. **5-Day Work Week Volume**: 216,000 * 5 = 1,080,000 requests.
> 
> **Final Answer**: 1,080,000 requests.

### Analysis
Direct prompting caused the model to hallucinate intermediate state arithmetic, leading to a wrong calculation. Explicitly instructing the model to "think step by step" allowed it to decompose the time conversions correctly and yield the exact correct value ($1,080,000$).

---

## 3. Structured Output Extraction (JSON)

### Target JSON Schema
```json
{
  "customer_name": "string",
  "purchase_date": "YYYY-MM-DD",
  "amount_paid": "number",
  "currency": "string",
  "issue_reported": "boolean"
}
