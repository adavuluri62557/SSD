const express = require('express');
const app = express();
app.use(express.json());

app.post('/calculate', (req, res) => {
  const expression = req.body.expression;

  // VULNERABLE: eval() runs whatever string the client sends
  const result = eval(expression);

  res.json({ result: result });
});

app.listen(3001, () => {
  console.log('Vulnerable calculator running at http://localhost:3001');
});
