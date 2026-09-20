const express = require('express');
const { evaluate } = require('mathjs');
const app = express();
app.use(express.json());

app.post('/calculate', (req, res) => {
  const expression = req.body.expression;

  try {
    const result = evaluate(expression); // mathjs can't reach require/process/fs
    res.json({ result: result });
  } catch (err) {
    res.status(400).json({ error: 'Invalid expression' });
  }
});

app.listen(3001, () => {
  console.log('Fixed calculator running at http://localhost:3001');
});
