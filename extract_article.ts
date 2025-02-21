const { Readability } = require('@mozilla/readability');
const { JSDOM } = require('jsdom');
const fs = require('fs');

const url = process.argv[2];
const ARTICLE_FILE = 'extracted_article.txt';
const ARTICLE_TITLE_FILE = 'extracted_article_title.txt';

if (!url) {
    console.error('Provide a URL or local file path as an argument');
    process.exit(1);
}

async function extractContent(url: string) {
    const article_fd = fs.openSync(ARTICLE_FILE, 'w');
    const title_fd = fs.openSync(ARTICLE_TITLE_FILE, 'w');
    try {
        let dom: any;
        if (url.startsWith('http')) {
            dom = await JSDOM.fromURL(url);
        } else {
            const fileContent = fs.readFileSync(url, 'utf8');
            dom = new JSDOM(fileContent);
        }
        const reader = new Readability(dom.window.document);
        const article = reader.parse();
        fs.writeFileSync(article_fd, article.textContent, 'utf8');
        fs.writeFileSync(title_fd, article.title, 'utf8');
    } catch (error: unknown) {
        if (error instanceof Error) {
            console.error('Error:', error.message);
        } else {
            console.error('An unknown error occurred');
        }
        process.exit(1);
    } finally {
        fs.closeSync(article_fd);
        fs.closeSync(title_fd);
    }
}

extractContent(url);
