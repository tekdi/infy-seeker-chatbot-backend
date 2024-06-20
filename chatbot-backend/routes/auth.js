const express = require("express");
const fs = require("fs");
const path = require("path");
const router = express.Router();

const usersFilePath = path.join(__dirname, "..", "data", "users.json");

// Create users.json if it doesn't exist
if (!fs.existsSync(usersFilePath)) {
  fs.writeFileSync(usersFilePath, JSON.stringify([]));
}

router.post("/signup", (req, res) => {
  const { fullname, email, password } = req.body;
  const users = JSON.parse(fs.readFileSync(usersFilePath, "utf-8"));
  if (users.find((user) => user.email === email)) {
    return res.status(400).json({ message: "User already exists" });
  }
  users.push({ fullname, email, password });
  fs.writeFileSync(usersFilePath, JSON.stringify(users, null, 2));
  res.status(201).json({ message: "User created" });
});

router.post("/signin", (req, res) => {
  const { email, password } = req.body;
  const users = JSON.parse(fs.readFileSync(usersFilePath, "utf-8"));
  const user = users.find(
    (user) => user.email === email && user.password === password
  );
  if (!user) {
    return res.status(400).json({ message: "Invalid credentials" });
  }
  res.status(200).json({ message: "User signed in" });
});

module.exports = router;
