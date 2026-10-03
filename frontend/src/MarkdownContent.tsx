import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

function prepareText(text: string): string {
  return text.replace(/\[([^\]\s]+\.(txt|md|yaml|yml))\]/g, "`$1`");
}

export function MarkdownContent({ text }: { text: string }) {
  return (
    <div className="md-content">
      <ReactMarkdown remarkPlugins={[remarkGfm]}>{prepareText(text)}</ReactMarkdown>
    </div>
  );
}
