//Import dependnecies
let path = require("path");

//Import configuration file
let config = require(path.join(process.cwd(), "config.json"));

//Print project
process.stdout.write(config["project"])

