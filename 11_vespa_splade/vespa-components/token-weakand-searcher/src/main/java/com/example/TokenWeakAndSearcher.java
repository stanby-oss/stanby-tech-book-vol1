package com.example;

import com.yahoo.language.Language;
import com.yahoo.language.Linguistics;
import com.yahoo.language.process.StemMode;
import com.yahoo.language.process.Token;
import com.yahoo.language.process.Tokenizer;
import com.yahoo.prelude.query.WeakAndItem;
import com.yahoo.prelude.query.WordItem;
import com.yahoo.search.Query;
import com.yahoo.search.Result;
import com.yahoo.search.searchchain.Execution;
import com.yahoo.search.Searcher;

/**
 * TokenWeakAndSearcher (WAND版)
 * トークナイズ後の各トークンを WAND(weakAnd) で OR ライクにマッチングする。
 */
public class TokenWeakAndSearcher extends Searcher {

    private final Linguistics linguistics;

    public TokenWeakAndSearcher(Linguistics linguistics) {
        this.linguistics = linguistics;
    }

    @Override
    public Result search(Query query, Execution execution) {
        // 入力文字列取得
        String input = query.properties().getString("userInput");
        if (input == null || input.isEmpty()) {
            query.trace("userInput is null", false, 2);
            return execution.search(query);
        }
        int hits = query.getHits();
        Language language = query.getModel().getParsingLanguage();
        query.trace("TokenWeakAndSearcher input " + input, false, 2);

        // トークナイズ
        Tokenizer tokenizer = linguistics.getTokenizer();
        Iterable<Token> tokens = tokenizer.tokenize(
                input,
                language,
                StemMode.NONE,
                false);

        WeakAndItem weakAnd = new WeakAndItem(hits);
        for (Token token : tokens) {
            if (!token.isIndexable())
                continue;
            weakAnd.addItem(new WordItem(token.getTokenString()));
        }
        query.trace("weakAnd " + weakAnd.toString(), false, 2);

        // ルート置換
        query.getModel().getQueryTree().setRoot(weakAnd);

        // 次の Searcher 実行
        return execution.search(query);
    }
}
