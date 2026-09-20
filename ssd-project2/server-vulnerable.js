const express = require('express');
const app = express();

app.get('/search', (req, res) => {
  const query = req.query.q || '';

  // VULNERABLE: raw user input embedded directly into HTML
  res.send(`
    <html>
      <body>
        <h1>Search Results</h1>
        <p>You searched for: ${query}</p>
      </body>
    </html>
  `);
});

app.listen(3000, () => {
  console.log('Vulnerable server running at http://localhost:3000');
  console.log('Try: http://localhost:3000/search?q=<script>alert(1)</script>');
});
