"""Patch LMCache connectors to support vLLM's hybrid KV cache manager (HMA).

Adds the SupportsHMA mixin to LMCacheConnectorV1Dynamic in ALL connector
files so that vLLM's hybrid KV cache allocator works with LMCache. This
enables sliding-window layers to allocate only their window size instead
of the full context.

See: https://github.com/LMCache/LMCache/pull/2863
"""

import importlib

CONNECTOR_MODULES = [
    "lmcache.integration.vllm.lmcache_connector_v1",
    "lmcache.integration.vllm.lmcache_connector_v1_085",
]

for module_name in CONNECTOR_MODULES:
    try:
        mod = importlib.import_module(module_name)
    except ImportError:
        print(f"Skipping {module_name} (not found)")
        continue

    path = mod.__file__
    with open(path) as f:
        src = f.read()

    if "SupportsHMA" in src:
        print(f"Already patched: {path}")
        continue

    # Add SupportsHMA import
    src = src.replace(
        "from vllm.distributed.kv_transfer.kv_connector.v1.base import (\n"
        "    KVConnectorBase_V1,",
        "from vllm.distributed.kv_transfer.kv_connector.v1.base import (\n"
        "    KVConnectorBase_V1,\n"
        "    SupportsHMA,",
    )

    # Add SupportsHMA to class bases
    src = src.replace(
        "class LMCacheConnectorV1Dynamic(KVConnectorBase_V1):",
        "class LMCacheConnectorV1Dynamic(KVConnectorBase_V1, SupportsHMA):",
    )

    # Add request_finished_all_groups method after request_finished
    src = src.replace(
        "        return self._lmcache_engine.request_finished(request, block_ids)\n",
        '        return self._lmcache_engine.request_finished(request, block_ids)\n'
        "\n"
        "    def request_finished_all_groups(\n"
        "        self,\n"
        '        request: "Request",\n'
        "        block_ids: tuple[list[int], ...],\n"
        "    ) -> tuple[bool, dict[str, Any] | None]:\n"
        '        """HMA support: flatten multi-group block IDs and delegate."""\n'
        "        flat_ids = [bid for group in block_ids for bid in group]\n"
        "        return self._lmcache_engine.request_finished(request, flat_ids)\n",
    )

    with open(path, "w") as f:
        f.write(src)

    print(f"Patched {path} with SupportsHMA support")
