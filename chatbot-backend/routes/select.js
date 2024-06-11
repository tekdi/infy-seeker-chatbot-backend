const express = require("express");
const router = express.Router();
const axios = require("axios");

const SELECT_ENDPOINT = "https://kahani-api.tekdinext.com/select";

router.post("/", async (req, res) => {
  const payload = req.body;

  console.log("Received payload:", JSON.stringify(payload, null, 2));

  try {
    const response = await axios.post(SELECT_ENDPOINT, payload, {
      headers: {
        Accept: "application/json, text/plain, */*",
        "Content-Type": "application/json",
        Origin: "https://lexp-dev.tekdinext.com",
      },
    });

    res.json(response.data);
  } catch (error) {
    console.error("Error calling select API:", error);
    res.status(500).json({
      status: "error",
      message: "Enrollment failed. Please try again.",
    });
  }
});

module.exports = router;
