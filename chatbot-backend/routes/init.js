const express = require("express");
const router = express.Router();
const axios = require("axios");

const INIT_ENDPOINT = "https://kahani-api.tekdinext.com/init";

router.post("/", async (req, res) => {
  console.log("Received request body:", req.body);

  try {
    const response = await axios.post(INIT_ENDPOINT, req.body, {
      headers: {
        "Content-Type": "application/json",
      },
    });

    console.log("Response data:", JSON.stringify(response.data, null, 2));
    res.json(response.data);
  } catch (error) {
    console.error(
      "Error:",
      error.response ? error.response.data : error.message
    );
    res.status(500).json({ status: "error", message: "Internal Server Error" });
  }
});

module.exports = router;
