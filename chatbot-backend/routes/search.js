const express = require("express");
const router = express.Router();
const axios = require("axios");

const API_ENDPOINT = "https://kahani-api.tekdinext.com/content/search";

router.post("/", async (req, res) => {
  const userInput = req.body;
  console.log("Received data for search:", userInput);

  try {
    const titles = userInput.results
      .map((item) => item.kahani_cache_dev__title)
      .join(" ");
    const transformedData = { title: titles };
    console.log(transformedData);

    const response = await axios.post(API_ENDPOINT, transformedData);
    res.json(response.data);
  } catch (error) {
    console.error("Error:", error);
    res.status(500).json({ error: "Internal Server Error" });
  }
});

module.exports = router;
