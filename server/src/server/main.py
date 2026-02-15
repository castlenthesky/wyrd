import logging
import urllib.parse

from lsprotocol.types import (
    TEXT_DOCUMENT_DID_SAVE,
    DidSaveTextDocumentParams,
)
from pygls.lsp.server import LanguageServer
from server.db import FalkorDBClient
from server.parser import TreeSitterParser
from server.uast.builder import UASTBuilder
from server.uast.ingester import UASTIngester

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

server = LanguageServer("wyrd-server", "v0.1")

# Initialize components
parser = TreeSitterParser()
uast_builder = UASTBuilder()
db_client = FalkorDBClient()
ingester = UASTIngester(db_client)


@server.feature(TEXT_DOCUMENT_DID_SAVE)
def did_save(ls: LanguageServer, params: DidSaveTextDocumentParams):
    uri = params.text_document.uri

    # Read file content from disk
    content = None
    if uri.startswith("file://"):
        file_path = urllib.parse.unquote(uri[7:])  # Simple unquote for now
        try:
            with open(file_path, "r") as f:
                content = f.read()
        except Exception as e:
            logger.error(f"Failed to read file {file_path}: {e}")
            return

    if content:
        logger.info(f"Parsing file: {uri}")

        # 1. Parse to CST (using TreeSitterParser helper or direct)
        tree = parser.parse(content)

        # 2. Build UAST
        # Pass the source code bytes
        graph_payload = uast_builder.build(tree.root_node, bytes(content, "utf8"))
        logger.info(
            f"Built UAST with {len(graph_payload.nodes)} nodes and {len(graph_payload.edges)} edges"
        )

        # 3. Ingest to FalkorDB
        if not db_client.graph:
            if not db_client.connect():
                logger.error("No DB connection")
                return

        try:
            # TODO: Implement robust deletion strategy.
            # For now, we rely on MERGE idempotency.

            ingester.ingest(graph_payload)

            logger.info("Graph update complete")
            # Notify client to refresh graph
            ls.protocol.notify("wyrd/graphUpdated", {})

        except Exception as e:
            logger.error(f"DB Error: {e}")


@server.feature("wyrd/getGraph")
def get_graph(ls: LanguageServer, params):
    logger.info("Received request for full graph")
    if not db_client.graph:
        if not db_client.connect():
            logger.error("No DB connection")
            return {"nodes": [], "links": []}

    return db_client.get_full_graph()


def main():
    server.start_io()


if __name__ == "__main__":
    main()
