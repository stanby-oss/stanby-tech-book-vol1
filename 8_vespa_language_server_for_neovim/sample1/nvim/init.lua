-- 1. Vespa Language Server 用ファイルタイプを登録
vim.filetype.add {
  extension = {
    profile = 'sd',
    sd = 'sd',
    yql = 'yql'
  },
}

-- 2. Vespa LSP の設定を登録
vim.lsp.config['vespa_lsp'] = {
  cmd = { 'java', '-jar', '/root/vespa-language-server.jar' },
  root_dir = vim.fs.dirname(
    vim.fs.find({ 'schema.sd' }, { upward = true })[1]
  ),
  filetypes = { 'sd', 'yql' },
}

-- 3. Vespa LSP を有効化
vim.lsp.enable('vespa_lsp')
