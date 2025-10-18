# API Reference

## `/ask`

- **Method:** POST
- **Body:**
  ```json
  {
    "question": "Your question here"
  }
  ```
- **Response:**
  ```json
  {
    "answer": "The answer to your question",
    "sources": [
      {
        "url": "URL of the source document",
        "title": "Title of the source document"
      }
    ]
  }
  ```
