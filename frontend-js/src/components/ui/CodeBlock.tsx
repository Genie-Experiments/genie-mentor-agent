import React, { useEffect, useState } from 'react';
import { Check, Copy } from 'lucide-react';
import { createHighlighter } from 'shiki';

interface CodeBlockProps {
  code: string;
  language: string;
}

// Helper function to ensure we use a supported language
const getSafeLanguage = (language: string) => {
  // Common languages and their aliases
  const languageMap: Record<string, string> = {
    js: 'javascript',
    jsx: 'javascript',
    ts: 'typescript',
    tsx: 'typescript',
    py: 'python',
    sh: 'shell',
    bash: 'shell',
    md: 'markdown',
    yml: 'yaml',
  };

  // Try to map the language to a known one
  const mappedLanguage = languageMap[language] || language;

  // List of languages we're preloading in the highlighter
  const supportedLanguages = [
    'javascript',
    'typescript',
    'python',
    'java',
    'go',
    'rust',
    'json',
    'html',
    'css',
    'shell',
    'markdown',
    'yaml',
    'plaintext',
  ];

  return supportedLanguages.includes(mappedLanguage) ? mappedLanguage : 'plaintext';
};

const CodeBlock: React.FC<CodeBlockProps> = ({ code, language }) => {
  const [highlightedCode, setHighlightedCode] = useState('');
  const [copied, setCopied] = useState(false);

  useEffect(() => {
    const highlightCode = async () => {
      try {
        const highlighter = await createHighlighter({
          langs: [
            'javascript',
            'typescript',
            'python',
            'java',
            'go',
            'rust',
            'json',
            'html',
            'css',
            'shell',
            'markdown',
            'yaml',
            'plaintext',
          ],
          themes: ['github-dark'],
        });

        // Use a safe language or fall back to plaintext
        const safeLanguage = getSafeLanguage(language);

        const html = highlighter.codeToHtml(code, {
          lang: safeLanguage,
          theme: 'github-dark',
        });
        setHighlightedCode(html);
      } catch (error) {
        console.error('Error highlighting code:', error);
        // Fallback: display code without highlighting
        setHighlightedCode(`<pre>${code}</pre>`);
      }
    };

    highlightCode();
  }, [code, language]);

  const copyToClipboard = async () => {
    try {
      await navigator.clipboard.writeText(code);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (error) {
      console.error('Failed to copy code to clipboard:', error);
    }
  };

  return (
    <div className="mb-4 overflow-hidden rounded-md">
      <div className="flex items-center justify-between bg-[#161b22] px-4 py-1.5">
        <span className="font-mono text-xs text-gray-300">{language}</span>
        <button
          onClick={copyToClipboard}
          className="flex items-center gap-1 text-xs text-gray-300 transition-colors hover:text-white"
          aria-label={copied ? 'Copied!' : 'Copy code'}
        >
          {copied ? (
            <>
              <Check size={14} />
              <span>Copied!</span>
            </>
          ) : (
            <>
              <Copy size={14} />
              <span>Copy code</span>
            </>
          )}
        </button>
      </div>
      <div className="overflow-auto bg-[#0d1117] p-4">
        <div
          dangerouslySetInnerHTML={{ __html: highlightedCode }}
          className="shiki-code-container"
        />
      </div>
    </div>
  );
};

export default CodeBlock;
