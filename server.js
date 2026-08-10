const express = require('express');
const path = require('path');
const app = express();
const PORTA = process.env.PORT || 10000;

app.use(express.static(path.join(__dirname, '/')));

app.get('/', (req, res) => {
  res.sendFile(path.join(__dirname, 'index.html'));
});

app.listen(process.env.PORT || 3000, "0.0.0.0", () => {
  console.log('✅ Servidor rodando em http://localhost:' + PORTA);
});
