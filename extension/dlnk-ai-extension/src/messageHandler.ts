/**
 * Message Handler - Process and format messages
 * Handles markdown rendering, code extraction, and message formatting
 */

import { marked, Renderer } from 'marked';
import hljs from 'highlight.js';

// Create custom renderer for code highlighting
const renderer = new Renderer();
renderer.code = function(code: string, language: string | undefined): string {
    const lang = language || 'plaintext';
    if (lang && hljs.getLanguage(lang)) {
        try {
            const highlighted = hljs.highlight(code, { language: lang }).value;
            return `<pre><code class="hljs language-${lang}">${highlighted}</code></pre>`;
        } catch {
            // Fall through to auto-detection
        }
    }
    try {
        const highlighted = hljs.highlightAuto(code).value;
        return `<pre><code class="hljs">${highlighted}</code></pre>`;
    } catch {
        return `<pre><code>${code}</code></pre>`;
    }
};

// Configure marked
marked.setOptions({
    renderer: renderer,
    breaks: true,
    gfm: true
});

export interface CodeBlock {
    language: string;
    code: string;
    startLine: number;
    endLine: number;
}

export interface ProcessedMessage {
    html: string;
    codeBlocks: CodeBlock[];
    hasCode: boolean;
}

/**
 * Process message content and convert to HTML
 */
export function processMessage(content: string): ProcessedMessage {
    const codeBlocks = extractCodeBlocks(content);
    const html = marked.parse(content) as string;
    
    return {
        html,
        codeBlocks,
        hasCode: codeBlocks.length > 0
    };
}

/**
 * Extract code blocks from markdown content
 */
export function extractCodeBlocks(content: string): CodeBlock[] {
    const codeBlocks: CodeBlock[] = [];
    const codeBlockRegex = /```(\w*)\n([\s\S]*?)```/g;
    const lines = content.split('\n');
    
    let match;
    while ((match = codeBlockRegex.exec(content)) !== null) {
        const language = match[1] || 'plaintext';
        const code = match[2].trim();
        
        // Find line numbers
        const beforeMatch = content.substring(0, match.index);
        const startLine = beforeMatch.split('\n').length;
        const endLine = startLine + code.split('\n').length - 1;
        
        codeBlocks.push({
            language,
            code,
            startLine,
            endLine
        });
    }
    
    return codeBlocks;
}

/**
 * Format code with syntax highlighting
 */
export function formatCode(code: string, language: string): string {
    if (language && hljs.getLanguage(language)) {
        try {
            return hljs.highlight(code, { language }).value;
        } catch {
            // Fall through
        }
    }
    
    try {
        return hljs.highlightAuto(code).value;
    } catch {
        return escapeHtml(code);
    }
}

/**
 * Escape HTML special characters
 */
export function escapeHtml(text: string): string {
    const map: Record<string, string> = {
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#039;'
    };
    return text.replace(/[&<>"']/g, m => map[m]);
}

/**
 * Detect programming language from code
 */
export function detectLanguage(code: string): string {
    try {
        const result = hljs.highlightAuto(code);
        return result.language || 'plaintext';
    } catch {
        return 'plaintext';
    }
}

/**
 * Format timestamp for display
 */
export function formatTimestamp(date: Date): string {
    const now = new Date();
    const diff = now.getTime() - date.getTime();
    
    // Less than 1 minute
    if (diff < 60000) {
        return 'Just now';
    }
    
    // Less than 1 hour
    if (diff < 3600000) {
        const minutes = Math.floor(diff / 60000);
        return `${minutes}m ago`;
    }
    
    // Less than 24 hours
    if (diff < 86400000) {
        const hours = Math.floor(diff / 3600000);
        return `${hours}h ago`;
    }
    
    // Same year
    if (date.getFullYear() === now.getFullYear()) {
        return date.toLocaleDateString(undefined, { month: 'short', day: 'numeric' });
    }
    
    // Different year
    return date.toLocaleDateString(undefined, { year: 'numeric', month: 'short', day: 'numeric' });
}

/**
 * Truncate text with ellipsis
 */
export function truncateText(text: string, maxLength: number): string {
    if (text.length <= maxLength) {
        return text;
    }
    return text.substring(0, maxLength - 3) + '...';
}

/**
 * Strip markdown formatting
 */
export function stripMarkdown(text: string): string {
    return text
        .replace(/```[\s\S]*?```/g, '[code]')
        .replace(/`[^`]+`/g, '[code]')
        .replace(/\*\*([^*]+)\*\*/g, '$1')
        .replace(/\*([^*]+)\*/g, '$1')
        .replace(/__([^_]+)__/g, '$1')
        .replace(/_([^_]+)_/g, '$1')
        .replace(/#+\s*/g, '')
        .replace(/\[([^\]]+)\]\([^)]+\)/g, '$1')
        .replace(/!\[([^\]]*)\]\([^)]+\)/g, '[image]')
        .trim();
}

/**
 * Create message preview for history
 */
export function createMessagePreview(content: string, maxLength: number = 50): string {
    const stripped = stripMarkdown(content);
    return truncateText(stripped, maxLength);
}
