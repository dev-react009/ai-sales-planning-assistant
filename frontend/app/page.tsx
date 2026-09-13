"use client";

import { useEffect, useRef, useState } from "react";
import { Bot, Send, Sparkles, User } from "lucide-react";
import {
  Collapsible,
  CollapsibleContent,
  CollapsibleTrigger,
} from "@/components/ui/collapsible";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Separator } from "@/components/ui/separator";
import { Textarea } from "@/components/ui/textarea";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

type ChatResponse = {
  answer: string;
  route: string;
  sources: string[];
  tools_used: string[];
};

type ChatMessage = {
  id: string;
  role: "user" | "assistant";
  content: string;
  route?: string;
  sources?: string[];
  tools_used?: string[];
};

const suggestedQuestions = [
  "What is the territory allocation policy?",
  "Which sales reps are below 70% quota?",
  "Show me unassigned enterprise accounts.",
  "Find unassigned enterprise accounts and recommend potential territories based on the territory allocation policy.",
];

const API_URL =
  process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";

function getRouteLabel(route?: string) {
  switch (route) {
    case "rag":
      return "RAG";

    case "tool":
      return "Tool";

    case "rag_and_tool":
      return "RAG + Tool";

    default:
      return route || "AI";
  }
}

function getRouteVariant(
  route?: string
): "default" | "secondary" | "outline" {
  switch (route) {
    case "rag_and_tool":
      return "default";

    case "tool":
      return "secondary";

    default:
      return "outline";
  }
}

export default function Home() {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [question, setQuestion] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({
      behavior: "smooth",
    });
  }, [messages, loading]);

  async function sendMessage(message?: string) {
    const userQuestion = (message ?? question).trim();

    if (!userQuestion || loading) {
      return;
    }

    const userMessage: ChatMessage = {
      id: crypto.randomUUID(),
      role: "user",
      content: userQuestion,
    };

    setMessages((previous) => [...previous, userMessage]);
    setQuestion("");
    setError("");
    setLoading(true);

    try {
      const response = await fetch(`${API_URL}/api/chat`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          question: userQuestion,
        }),
      });

      if (!response.ok) {
        throw new Error("API request failed");
      }

      const data: ChatResponse = await response.json();

      const assistantMessage: ChatMessage = {
        id: crypto.randomUUID(),
        role: "assistant",
        content: data.answer,
        route: data.route,
        sources: data.sources ?? [],
        tools_used: data.tools_used ?? [],
      };

      setMessages((previous) => [
        ...previous,
        assistantMessage,
      ]);
    } catch {
      setError(
        "Unable to connect to the AI assistant. Make sure the FastAPI backend is running."
      );
    } finally {
      setLoading(false);

      setTimeout(() => {
        textareaRef.current?.focus();
      }, 0);
    }
  }

  function handleKeyDown(
    event: React.KeyboardEvent<HTMLTextAreaElement>
  ) {
    if (event.key === "Enter" && !event.shiftKey) {
      event.preventDefault();
      void sendMessage();
    }
  }

  return (
    <main className="min-h-screen bg-background">
      <div className="mx-auto flex min-h-screen w-full max-w-6xl flex-col px-4 py-6 sm:px-6 lg:px-8">
        {/* Header */}
        <header className="mb-6">
          <div className="flex items-center gap-3">
            <div className="flex h-11 w-11 items-center justify-center rounded-xl bg-primary text-primary-foreground shadow-sm">
              <Sparkles className="h-5 w-5" />
            </div>

            <div>
              <h1 className="text-xl font-semibold tracking-tight sm:text-2xl">
                AI Sales Planning Assistant
              </h1>

              <p className="text-sm text-muted-foreground">
                Ask questions about sales policies, territories,
                quotas, and accounts.
              </p>
            </div>
          </div>
        </header>

        {/* Main Chat Card */}
        <Card className="flex min-h-[calc(100vh-150px)] flex-1 flex-col overflow-hidden shadow-sm">
          <CardHeader className="border-b bg-muted/20 px-4 py-4 sm:px-6">
            <div className="flex items-center justify-between">
              <CardTitle className="text-sm font-medium">
                Sales Intelligence
              </CardTitle>

              <Badge variant="outline" className="gap-1">
                <span className="h-1.5 w-1.5 rounded-full bg-green-500" />
                AI Decision Support
              </Badge>
            </div>
          </CardHeader>

          <CardContent className="flex flex-1 flex-col p-0">
            {/* Chat */}
            <ScrollArea className="flex-1 px-4 sm:px-8">
              <div className="mx-auto max-w-4xl py-8">
                {messages.length === 0 ? (
                  <EmptyState
                    onSelectQuestion={(selectedQuestion) =>
                      void sendMessage(selectedQuestion)
                    }
                  />
                ) : (
                  <div className="space-y-6">
                    {messages.map((message) => (
                      <ChatBubble
                        key={message.id}
                        message={message}
                      />
                    ))}

                    {loading && (
                      <div className="flex gap-3">
                        <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-full border bg-muted">
                          <Bot className="h-4 w-4" />
                        </div>

                        <div className="rounded-2xl border bg-muted/50 px-4 py-3">
                          <div className="flex items-center gap-2 text-sm text-muted-foreground">
                            <span>Thinking</span>

                            <span className="flex gap-1">
                              <span className="h-1.5 w-1.5 animate-bounce rounded-full bg-current [animation-delay:-0.3s]" />
                              <span className="h-1.5 w-1.5 animate-bounce rounded-full bg-current [animation-delay:-0.15s]" />
                              <span className="h-1.5 w-1.5 animate-bounce rounded-full bg-current" />
                            </span>
                          </div>
                        </div>
                      </div>
                    )}

                    <div ref={bottomRef} />
                  </div>
                )}

                {error && (
                  <div className="mt-6 rounded-xl border border-destructive/30 bg-destructive/5 px-4 py-3 text-sm text-destructive">
                    {error}
                  </div>
                )}
              </div>
            </ScrollArea>

            <Separator />

            {/* Input */}
            <div className="bg-muted/10 p-5 sm:p-6">
              <div className="mx-auto max-w-4xl">
                <div className="relative rounded-xl border bg-background shadow-sm">
                  <Textarea
                    ref={textareaRef}
                    value={question}
                    onChange={(event) =>
                      setQuestion(event.target.value)
                    }
                    onKeyDown={handleKeyDown}
                    placeholder="Ask about territories, quotas, accounts..."
                    disabled={loading}
                    className="min-h-[40px] max-h-[160px] resize-none border-0 pr-16 shadow-none focus-visible:ring-0"
                  />
                  {!question && (
        <span className="pointer-events-none absolute bottom-3 right-12 text-[11px] text-muted-foreground/50">
          Enter to send · Shift + Enter for new line
        </span>
      )}

                  <Button
                    size="icon"
                    className="absolute bottom-1 right-1"
                    onClick={() => void sendMessage()}
                    disabled={!question.trim() || loading}
                    aria-label="Send message"
                  >
                    <Send className="h-4 w-4" />
                  </Button>
                </div>

                
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </main>
  );
}

function EmptyState({
  onSelectQuestion,
}: {
  onSelectQuestion: (question: string) => void;
}) {
  return (
    <div className="flex min-h-[500px] flex-col items-center justify-center text-center">
      <div className="mb-5 flex h-14 w-14 items-center justify-center rounded-2xl border bg-muted/40">
        <Bot className="h-7 w-7" />
      </div>

      <h2 className="text-2xl font-semibold tracking-tight">
        How can I help with sales planning?
      </h2>

      <p className="mt-2 max-w-lg text-sm leading-6 text-muted-foreground">
        I can search company policies, analyze current sales
        data, and combine both to provide decision-support
        recommendations.
      </p>

      <div className="mt-8 grid w-full max-w-3xl gap-3 sm:grid-cols-2">
        {suggestedQuestions.map((item) => (
          <button
            key={item}
            type="button"
            onClick={() => onSelectQuestion(item)}
            className="rounded-xl border bg-background p-4 text-left text-sm transition-colors hover:bg-muted/50"
          >
            <span className="font-medium">{item}</span>

            <span className="mt-2 block text-xs text-muted-foreground">
              Ask assistant
            </span>
          </button>
        ))}
      </div>
    </div>
  );
}

function ChatBubble({
  message,
}: {
  message: ChatMessage;
}) {
  const isUser = message.role === "user";

  return (
    <div
      className={`flex gap-3 ${
        isUser ? "flex-row-reverse" : ""
      }`}
    >
      <div
        className={`flex h-9 w-9 shrink-0 items-center justify-center rounded-full border ${
          isUser
            ? "bg-primary text-primary-foreground"
            : "bg-muted"
        }`}
      >
        {isUser ? (
          <User className="h-4 w-4" />
        ) : (
          <Bot className="h-4 w-4" />
        )}
      </div>

      <div
        className={`max-w-[85%] space-y-3 sm:max-w-[75%] ${
          isUser ? "items-end" : ""
        }`}
      >
        <div
          className={`rounded-2xl px-4 py-3 text-sm leading-6 ${
            isUser
              ? "bg-primary text-primary-foreground"
              : "border bg-muted/40"
          }`}
        >
         {isUser ? (
  <div className="whitespace-pre-wrap">
    {message.content}
  </div>
) : (
  <div className=" space-y-3 p-2">
    <ReactMarkdown
      remarkPlugins={[remarkGfm]}
      components={{

        table: ({ children }) => (
  <div className="my-4 w-full overflow-x-auto rounded-lg border">
    <table className="w-full  border-collapse text-sm">
      {children}
    </table>
  </div>
),

thead: ({ children }) => (
  <thead className="bg-muted/50">
    {children}
  </thead>
),

th: ({ children }) => (
  <th className="whitespace-nowrap border-b px-4 py-3 text-left font-semibold">
    {children}
  </th>
),

td: ({ children }) => (
  <td className="border-b px-4 py-3 align-top">
    {children}
  </td>
),

tr: ({ children }) => (
  <tr className="hover:bg-muted/30">
    {children}
  </tr>
),


        h1: ({ children }) => (
          <h1 className="text-xl font-semibold">
            {children}
          </h1>
        ),

        h2: ({ children }) => (
          <h2 className="text-lg font-semibold">
            {children}
          </h2>
        ),

        h3: ({ children }) => (
          <h3 className="font-semibold">
            {children}
          </h3>
        ),

        p: ({ children }) => (
          <p className="leading-6">
            {children}
          </p>
        ),

        ul: ({ children }) => (
          <ul className="list-disc space-y-1 pl-5">
            {children}
          </ul>
        ),

        ol: ({ children }) => (
          <ol className="list-decimal space-y-1 pl-5">
            {children}
          </ol>
        ),

        li: ({ children }) => (
          <li>{children}</li>
        ),

        strong: ({ children }) => (
          <strong className="font-semibold">
            {children}
          </strong>
        ),

        code: ({ children }) => (
          <code className="rounded bg-muted px-1.5 py-0.5 text-xs">
            {children}
          </code>
        ),
      }}
    >
      {message.content}
    </ReactMarkdown>
  </div>
)}
        </div>

        {!isUser && (
          <AssistantMetadata message={message} />
        )}
      </div>
    </div>
  );
}


function AssistantMetadata({
  message,
}: {
  message: ChatMessage;
}) {
  const hasSources =
    message.sources && message.sources.length > 0;

  const hasTools =
    message.tools_used && message.tools_used.length > 0;

  if (!message.route && !hasSources && !hasTools) {
    return null;
  }

  return (
    <Collapsible className="px-1">
      <CollapsibleTrigger className="text-xs text-muted-foreground transition-colors hover:text-foreground">
        View sources & analysis
      </CollapsibleTrigger>

      <CollapsibleContent className="mt-3 space-y-3">
        {message.route && (
          <div className="flex flex-wrap items-center gap-2">
            <span className="text-xs font-medium text-muted-foreground">
              Analysis
            </span>

            <Badge
              variant={getRouteVariant(message.route)}
              className="text-[11px]"
            >
              {getRouteLabel(message.route)}
            </Badge>
          </div>
        )}

        {hasSources && (
          <div className="space-y-2">
            <p className="text-xs font-medium text-muted-foreground">
              Sources
            </p>

            <div className="flex flex-wrap gap-2">
              {message.sources?.map((source) => (
                <Badge
                  key={source}
                  variant="outline"
                  className="text-[11px]"
                >
                  {source}
                </Badge>
              ))}
            </div>
          </div>
        )}

        {hasTools && (
          <div className="space-y-2">
            <p className="text-xs font-medium text-muted-foreground">
              Tools used
            </p>

            <div className="flex flex-wrap gap-2">
              {message.tools_used?.map((tool) => (
                <Badge
                  key={tool}
                  variant="secondary"
                  className="text-[11px]"
                >
                  {tool}
                </Badge>
              ))}
            </div>
          </div>
        )}
      </CollapsibleContent>
    </Collapsible>
  );
}