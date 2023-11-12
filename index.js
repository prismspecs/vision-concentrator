const express = require('express');
const fs = require('fs');
const app = express();
const translate = require('@iamtraction/google-translate');

const projectsDir = 'output/projects';
const configFilePath = 'current_config.dat';
const incomingFilename = 'incoming.dat';
let projectDir = "";

app.use(express.static('public'));
app.use(express.json());

// Serve the main admin page (index.html)
app.get('/', (req, res) => {
    res.sendFile(__dirname + '/public/index.html');
});

// Serve the input page (input.html)
app.get('/input', (req, res) => {
    res.sendFile(__dirname + '/public/input.html');

    // set projectDir
    // get projectName from current_config.dat
    projectDir = fs.readFileSync(configFilePath, 'utf-8');
    console.log("loaded projectDir: " + projectDir);
});

// Retrieve existing projects
app.get('/getProjects', (req, res) => {
    // Check if the projects directory exists
    if (!fs.existsSync(projectsDir)) {
        fs.mkdirSync(projectsDir);
    }

    const existingProjects = fs.readdirSync(projectsDir);
    res.json(existingProjects);
});

app.post('/createProject', (req, res) => {
    const projectName = req.body.projectName;
    const sanitizedProjectName = projectName.replace(/ /g, '_');
    projectDir = `${projectsDir}/${sanitizedProjectName}`;
    const incomingFilePath = `${projectDir}/${incomingFilename}`;

    if (!fs.existsSync(projectDir)) {
        fs.mkdirSync(projectDir);
        fs.writeFileSync(configFilePath, projectDir);

        // Create incoming.dat within that folder
        fs.writeFileSync(incomingFilePath, ''); // You can add content to the file if needed

        res.json({ success: true, projectDir });
    } else {
        res.json({ success: false, message: 'Project name already exists.' });
    }
});

// Select an existing project
app.post('/selectProject', (req, res) => {
    const selectedProject = req.body.selectedProject;
    projectDir = `${projectsDir}/${selectedProject}`;
    fs.writeFileSync(configFilePath, projectDir);
    res.json({ success: true, projectDir });
});

// Append incoming text to incoming.dat and save file
app.post('/appendIncoming', async (req, res) => {
    const incomingText = req.body.incomingText;
    const incomingFilePath = `${projectDir}/${incomingFilename}`;
    console.log(incomingFilePath);

    try {
        const translation = await translate(incomingText, { to: 'en' });
        const translatedText = translation.text;

        // Append the translated text to the file, which is in projectDir
        fs.appendFileSync(incomingFilePath, translatedText + '\n', 'utf-8');

        res.json({ success: true, incomingText, translatedText });
    } catch (error) {
        console.error('Translation error:', error);

        // If there's an error, append the original text
        fs.appendFileSync(incomingFilePath, incomingText + '\n', 'utf-8');

        // You may want to provide a more detailed error response here
        res.status(500).json({ success: false, error: error.message, incomingText });
    }
});

const port = process.env.PORT || 3000;
app.listen(port, () => {
    console.log(`Server is running on port ${port}`);
});