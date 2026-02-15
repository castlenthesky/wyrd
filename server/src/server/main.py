import logging
import urllib.parse

from lsprotocol.types import (
    TEXT_DOCUMENT_DID_SAVE,
    DidSaveTextDocumentParams,
)
from pygls.lsp.server import LanguageServer
from server.db import FalkorDBClient
from server.parser import TreeSitterParser

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

server = LanguageServer("wyrd-server", "v0.1")

# Initialize components
parser = TreeSitterParser()
db_client = FalkorDBClient()


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
        tree = parser.parse(content)
        nodes, edges = parser.extract_graph(tree, uri)

        logger.info(f"Extracted {len(nodes)} nodes and {len(edges)} edges")

        # DB Integration
        if not db_client.graph:
            if not db_client.connect():
                logger.error("No DB connection")
                return

        try:
            # 1. DELETE existing nodes for this file
            delete_query = f"MATCH (n {{file: '{uri}'}}) DETACH DELETE n"
            db_client.query(delete_query)

            # 2. CREATE nodes
            for node in nodes:
                props = node["properties"]
                # Add the ID to properties for easier querying
                props["node_id"] = node["id"]

                # Format properties for Cypher
                # Basic escaping for POC
                props_str_parts = []
                for k, v in props.items():
                    if isinstance(v, str):
                        safe_v = v.replace("'", "\\'")
                        props_str_parts.append(f"{k}: '{safe_v}'")
                    else:
                        props_str_parts.append(f"{k}: {v}")
                props_str = ", ".join(props_str_parts)

                query = f"CREATE (n:{node['label']} {{{props_str}}})"
                db_client.query(query)

            # 3. CREATE edges
            for src_id, rel_type, dst_id in edges:
                # MATCH using the node_id property
                # Using MERGE to be safe, though CREATE is faster if we are sure
                edge_query = f"""
                MATCH (a {{node_id: '{src_id}'}}), (b {{node_id: '{dst_id}'}})
                CREATE (a)-[:{rel_type}]->(b)
                """
                db_client.query(edge_query)

            logger.info("Graph update complete")
            # Notify client to refresh graph
            # ls.show_message("Graph updated", 1)  # Removed to avoid error and redundancy
            # Use protocol.notify for custom notifications in pygls v2+
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
