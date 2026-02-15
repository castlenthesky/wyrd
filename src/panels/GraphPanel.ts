import * as vscode from 'vscode';

export class GraphPanel {
  public static currentPanel: GraphPanel | undefined;
  private readonly _panel: vscode.WebviewPanel;
  private _disposables: vscode.Disposable[] = [];

  private constructor(panel: vscode.WebviewPanel, extensionUri: vscode.Uri) {
    this._panel = panel;
    this._panel.onDidDispose(() => this.dispose(), null, this._disposables);
    this._panel.webview.html = this._getWebviewContent();
    
    // Handle messages from the webview
    this._panel.webview.onDidReceiveMessage(
      message => {
        switch (message.command) {
          case 'alert':
            vscode.window.showErrorMessage(message.text);
            return;
        }
      },
      null,
      this._disposables
    );
  }

  public static createOrShow(extensionUri: vscode.Uri) {
    const column = vscode.window.activeTextEditor
      ? vscode.window.activeTextEditor.viewColumn
      : undefined;

    // If we already have a panel, show it.
    if (GraphPanel.currentPanel) {
      GraphPanel.currentPanel._panel.reveal(column);
      return;
    }

    // Otherwise, create a new panel.
    const panel = vscode.window.createWebviewPanel(
      'wyrdGraph',
      'Wyrd Graph',
      column || vscode.ViewColumn.One,
      {
        enableScripts: true,
        localResourceRoots: [vscode.Uri.joinPath(extensionUri, 'media')]
      }
    );

    GraphPanel.currentPanel = new GraphPanel(panel, extensionUri);
  }

  public updateGraph(graphData: any) {
    // Send data to the webview
    this._panel.webview.postMessage({ command: 'updateGraph', data: graphData });
  }

  public dispose() {
    GraphPanel.currentPanel = undefined;
    this._panel.dispose();
    while (this._disposables.length) {
      const x = this._disposables.pop();
      if (x) {
        x.dispose();
      }
    }
  }

  private _getWebviewContent() {
    return `<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta http-equiv="Content-Security-Policy" content="default-src 'none'; style-src 'unsafe-inline'; script-src 'unsafe-inline' 'unsafe-eval' https://unpkg.com;">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Wyrd Graph</title>
    <style>
        body { margin: 0; padding: 0; overflow: hidden; background-color: #000; color: #fff; }
        #graph { width: 100vw; height: 100vh; }
        .controls { position: absolute; top: 10px; left: 10px; z-index: 100; font-family: sans-serif; }
    </style>
    <script src="https://unpkg.com/force-graph"></script>
</head>
<body>
    <div class="controls">
        <h3>Wyrd Code Graph</h3>
        <p>Nodes: <span id="node-count">0</span> | Edges: <span id="edge-count">0</span></p>
    </div>
    <div id="graph"></div>

    <script>
        const graphElem = document.getElementById('graph');
        const Graph = ForceGraph()(graphElem)
            .backgroundColor('#101010')
            .nodeAutoColorBy('label')
            .nodeLabel(node => \`\${node.label}: \${node.name || node.id}\`)
            .linkLabel(link => link.label)
            .linkDirectionalArrowLength(3.5)
            .linkDirectionalArrowRelPos(1);

        // Handle messages sent from the extension to the webview
        window.addEventListener('message', event => {
            const message = event.data;
            switch (message.command) {
                case 'updateGraph':
                    const { nodes, links } = message.data;
                    document.getElementById('node-count').innerText = nodes.length;
                    document.getElementById('edge-count').innerText = links.length;
                    Graph.graphData(message.data);
                    break;
            }
        });
    </script>
</body>
</html>`;
  }
}
