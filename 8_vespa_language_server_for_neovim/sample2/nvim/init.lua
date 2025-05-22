-- 1. Vespa Language Server 用ファイルタイプを登録
vim.filetype.add {
    extension = {
        profile = 'sd',
        sd = 'sd',
        yql = 'yql',
    },
}

-- 2. Vespa LSP の設定を登録
local lspconfig = require "lspconfig"
local configs = require "lspconfig.configs"
if not configs.schemals then
    configs.schemals = {
        default_config = {
            filetypes = { 'sd' },
            cmd = { 'java', '-jar', '/root/vespa-language-server.jar' },
            root_dir = lspconfig.util.root_pattern('.')
        },
    }
end

-- 3. Vespa LSP を有効化
lspconfig.schemals.setup{}
