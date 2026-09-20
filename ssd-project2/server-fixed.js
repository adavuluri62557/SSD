const express = require('express');
const helmet = require('helmet');
const app = express();

app.set('view engine', 'ejs');
app.set('views', __dirname + '/views');

// CSP header - blocks inline scripts even if something slips through
app.use(helmet.contentSecurityPolicy({
  directives: {
    defaultSrc: ["'self'"],
    scriptSrc: ["'self'"],
    objectSrc: ["'none'"],
    baseUri: ["'self'"],
    styleSrc: ["'self'"],
  }
}));

app.get('/search', (req, res) => {
  const query = req.query.q || '';
  res.render('search', { query: query }); // <%= %> auto-escapes
});

app.listen(3000, () => {
  console.log('Fixed server running at http://localhost:3000');
  console.log('Try: http://localhost:3000/search?q=<script>alert(1)</script>');
});
