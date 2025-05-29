rank-profile weakand inherits default {
    inputs {
        query(q_splade) tensor<float>(token{})
    }

    function dot_product() {
        expression: sum(attribute(sparse_rep) * query(q_splade))
    }

    second-phase {
        rerank-count: 100
        # expression: dotProduct(attribute(sparse_rep), query(q_splade))
        expression: dot_product
    }

    summary-features {
        # dot_product
        attribute(sparse_rep)
        query(q_splade)
    }
}