export interface ToolResult {
  success: boolean;
  data?: any;
  error?: string;
  metadata?: Record<string, any>;
}

export interface Tool {
  name: string;
  description: string;
  parameters: Record<string, any>;
  execute: (...args: any[]) => Promise<ToolResult>;
}

export interface FileOperation {
  type: 'read' | 'write' | 'edit' | 'delete';
  path: string;
  content?: string;
  encoding?: string;
}

export interface SearchOptions {
  pattern: string;
  directory?: string;
  recursive?: boolean;
  fileTypes?: string[];
  ignoreCase?: boolean;
}

export interface CommandOptions {
  cwd?: string;
  timeout?: number;
  env?: Record<string, string>;
  shell?: string;
}

export interface SessionContext {
  workingDirectory: string;
  environment: Record<string, string>;
  history: string[];
  variables: Record<string, any>;
}