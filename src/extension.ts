import * as path from 'path';
import * as vscode from 'vscode';
import {
  LanguageClient,
  type LanguageClientOptions,
  type ServerOptions,
} from 'vscode-languageclient/node';

let client: LanguageClient;

export function activate(context: vscode.ExtensionContext) {
  console.log('Congratulations, your extension "wyrd" is now active!');

  const serverPath = context.asAbsolutePath(path.join('server'));

  // Use 'uv' to run the python server
  const run = {
    command: "uv",
    args: ["run", "python", "-m", "server.main"],
    options: { cwd: serverPath }
  };

  const serverOptions: ServerOptions = {
    run: run,
    debug: run
  };

  const clientOptions: LanguageClientOptions = {
    documentSelector: [{ scheme: 'file', language: 'python' }],
    synchronize: {
      fileEvents: vscode.workspace.createFileSystemWatcher('**/.clientrc')
    },
    outputChannelName: 'Wyrd Language Server'
  };

  client = new LanguageClient(
    'wyrd',
    'Wyrd Language Server',
    serverOptions,
    clientOptions
  );

  client.start();

  let disposable = vscode.commands.registerCommand('wyrd.helloWorld', () => {
    vscode.window.showInformationMessage('Hello World from Wyrd!');
  });

  context.subscriptions.push(disposable);
}

export function deactivate(): Thenable<void> | undefined {
  if (!client) {
    return undefined;
  }
  return client.stop();
}
