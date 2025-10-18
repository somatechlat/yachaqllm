# Quick-Start Tutorial

This tutorial will guide you through making your first query to the YACHAQ-LEX API.

## Prerequisites

- You have the IP address of the YACHAQ-LEX server.
- You have a tool for making HTTP requests, suchs as `curl` or Postman.

## Making a Query

To ask a question, send a POST request to the `/ask` endpoint with a JSON body containing your question.

```bash
curl -X POST -H "Content-Type: application/json" -d '{"question": "What are the requirements for importing goods into Ecuador?"}' http://<your_server_ip>:8000/ask
```
