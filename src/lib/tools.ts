export type ToolRegistryEntry = {
  icon: string,
  routeName: string
}

// Maps a tool's backend key (monsoon/models/tool.py) to the frontend route and icon that
// render it. A tool key with no entry here is simply not rendered in the tools list -- see
// Home.vue.
export const TOOL_REGISTRY: Record<string, ToolRegistryEntry> = {
  bulk_media_uploader: {
    icon: 'mdi-upload-multiple',
    routeName: 'BulkMediaUploader'
  }
}
