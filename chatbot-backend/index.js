const express = require("express");
const cors = require("cors");
const app = express();
const bodyParser = require('body-parser');
const authRoutes = require('./routes/auth');
// Middlewares
app.use(cors());
app.use(express.json());
app.use(bodyParser.json());
app.use((req, res, next) => {
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type, Authorization');
  next();
});

app.use(authRoutes);

// Routes
const searchRoute = require("./routes/search");
const selectRoute = require("./routes/select");
const initRoute = require("./routes/init");
const confirmRoute = require("./routes/confirm");

app.use("/search", searchRoute);
app.use("/select", selectRoute);
app.use("/init", initRoute);
app.use("/confirm", confirmRoute);

// Start server
const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
  console.log(`Server is running on port ${PORT}`);


});
