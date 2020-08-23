const express = require("express");
const app = express();
const port = 3000;
var bodyParser = require("body-parser");
var multer = require("multer");
var upload = multer({ dest: "./public/videos" });
var path = require("path");
const { spawn } = require("child_process");
const fs = require("fs");
const { exec } = require("child_process");
const directoryPath = path.join("/home/royer/jsons-temporal");
app.use(bodyParser.json());
app.use(bodyParser.urlencoded({ extended: true }));
app.use(function (req, res, next) {
  res.header("Access-Control-Allow-Origin", "*");
  res.header(
    "Access-Control-Allow-Headers",
    "Origin, X-Requested-With, Content-Type, Accept"
  );
  next();
});

var storage = multer.diskStorage({
  destination: function (request, file, callback) {
    callback(null, "./public/videos");
  },
  filename: function (request, file, callback) {
    console.log(file);
    callback(null, file.originalname);
  },
});

var upload = multer({ storage: storage });

app.get("/", (req, res) => {
  res.send("Hola Mundo");
});

app.post("/coordinates", upload.single("video"), (req, res, next) => {
  const file = req.file;
  if (!file) {
    const error = new Error("Please upload a file");
    error.httpStatusCode = 400;
    return next(error);
  }
  console.log(file);
  exec("cd ~ && ls", (error, stdout, stderr) => {
    if (error) {
      console.log(`error: ${error.message}`);
      return;
    }
    if (stderr) {
      console.log(`stderr: ${stderr}`);
      return;
    }
    console.log(`stdout: ${stdout}`);
    console.log("xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx");
    exec(
      "cd ~/openpose-server && rm public/videos/*",
      (error, stdout, stderr) => {
        if (error) {
          console.log(`error: ${error.message}`);
          return;
        }
        if (stderr) {
          console.log(`stderr: ${stderr}`);
          return;
        }
        console.log(`stdout: ${stdout}`);

        var coordinates;
        const python = spawn("python3", ["./public/scripts/script.py"]);
        python.stdout.on("data", function (data) {
          if (data.toString()[0] == "[") {
            coordinates = data.toString();
            coordinates = coordinates.substring(1, coordinates.length - 1);
            coordinates = coordinates.split(",").map(Number);
          }
        });
        python.on("close", (code) => {
          exec("cd ~ && rm jsons-temporal/* ", (error, stdout, stderr) => {
            if (error) {
              console.log(`error: ${error.message}`);
              return;
            }
            if (stderr) {
              console.log(`stderr: ${stderr}`);
              return;
            }
            console.log(`stdout: ${stdout}`);
            res.json({
              keypoints: coordinates,
            });
          });
        });
      }
    );
  });
});

app.get("/script", (req, res) => {
  var dataToSend;
  const python = spawn("python3", ["./public/scripts/script.py"]);
  python.stdout.on("data", function (data) {
    console.log("Pipe data from python script ...");
    console.log(data.toString());
    if (data.toString()[0] == "[") {
      dataToSend = data.toString();
      dataToSend = dataToSend.substring(1, dataToSend.length - 1);
      dataToSend = dataToSend.split(",").map(Number);
      console.log(dataToSend[dataToSend.length - 1]);
    }
  });
  python.on("close", (code) => {
    console.log(`child process close all stdio with code ${code}`);
    console.log(dataToSend);
    res.json({
      keypoints: dataToSend,
    });
  });
});

app.listen(port, () => {
  console.log(`Example app listening at http://localhost:${port}`);
});
