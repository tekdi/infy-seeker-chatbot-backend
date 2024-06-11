const express = require("express");
const cors = require("cors");
const app = express();

// Middlewares
app.use(cors());
app.use(express.json());

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
