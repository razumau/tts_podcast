const { Readability } = require('@mozilla/readability');
const { JSDOM } = require('jsdom');
const fs = require('fs');

const url = process.argv[2];
const ARTICLE_FILE = 'extracted_article.txt';
const ARTICLE_TITLE_FILE = 'extracted_article_title.txt';

if (!url) {
    console.error('Provide a URL as an argument');
    process.exit(1);
}

async function extractContent(url: string) {
    const article_fd = fs.openSync(ARTICLE_FILE, 'w');
    const title_fd = fs.openSync(ARTICLE_TITLE_FILE, 'w');
    try {
        const doc = await JSDOM.fromURL(url);
        const reader = new Readability(doc.window.document);
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
