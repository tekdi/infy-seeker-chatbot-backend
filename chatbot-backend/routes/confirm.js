const express = require("express");
const router = express.Router();
const axios = require("axios");

const CONFIRM_ENDPOINT = "https://kahani-api.tekdinext.com/confirm";

router.post("/", async (req, res) => {
  const confirmInput = req.body;
  console.log("Received data for confirm:", confirmInput);

  try {
    const response = await axios.post(CONFIRM_ENDPOINT, confirmInput);
    res.json(response.data);
  } catch (error) {
    console.error("Error:", error);
    res.status(500).json({ error: "Internal Server Error" });
  }
});

module.exports = router;
