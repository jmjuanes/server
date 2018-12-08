//Import dependencies
let fs = require("fs");
let path = require("path");
let handlebars = require("handlebars");

//Import configuration file
let config = require(path.join(process.cwd(), "config.json"));

//Build templates
process.nextTick(function () {
    //Load template file
    let templatePath = path.join(process.cwd(), config.static.template);
    let templateContent = fs.readFileSync(templatePath, "utf8");
    //Generate the handlebars template
    let template = handlebars.compile(templateContent);
    //Output static files path
    let staticFolder = path.join(process.cwd(), "static");
    //Chekc if the static folder exists
    if (fs.existsSync(staticFolder) === false) {
        fs.mkdirSync(staticFolder);
    }
    //Build each static file
    Object.keys(config.static.pages).forEach(function (key) {
        console.log("Building " + key + " template");
        //Generate the file content
        let content = template({
            "home": config.static.home,
            "links": Object.values(config.static.links),
            "page": config.static.pages[key]
        });
        //Save the static file
        let staticPath = path.join(staticFolder, key + ".html");
        fs.writeFileSync(staticPath, content, "utf8");
    });
    //Finish build
    console.log("Build finished");
});

